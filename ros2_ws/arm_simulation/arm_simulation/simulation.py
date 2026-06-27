#!/home/mohnc/ros2_ws/.env/bin/python3

import numpy as np
from geometry_msgs.msg import Point32
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy

from arm_simulation.home_config import HOME_POS, BASE_HEIGHT



class Simulation(Node):
    def __init__(self):
        super().__init__('simulation')

        qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
        )

        self.target_sub = self.create_subscription(
            Point32,
            'target_point',
            self.target_callback,
            qos,
        )
        self.joint_pub = self.create_publisher(Point32, 'joint_angles', qos)

        self.l1 = 200.0
        self.l2 = 200.0
        self.base_pos = np.array([0.0, 0.0, BASE_HEIGHT], dtype=float)
        self.home_pos = HOME_POS.copy()
        self.q_offset = self.ik_rrr_xyz(self.home_pos, elbow='down')
        self.elbow_mode = 'down'

        self.target = self.home_pos.copy()
        self.last_q_motor = np.zeros(3)
        self.unreachable = False

        self.timer = self.create_timer(0.05, self.timer_callback)
        self.get_logger().info(
            'simulation started: subscribing /target_point, publishing /joint_angles (Point32, best effort)'
        )

    def ik_rrr_xyz(self, p, elbow='down'):
        p_local = np.array(p, dtype=float) - self.base_pos

        x, y, z = float(p_local[0]), float(p_local[1]), float(p_local[2])
        q1 = np.arctan2(y, x)
        r = np.hypot(x, y)
        xp, zp = r, z

        d = (xp**2 + zp**2 - self.l1**2 - self.l2**2) / (2.0 * self.l1 * self.l2)
        eps = 1e-6
        if d < -1.0 - eps or d > 1.0 + eps:
            raise ValueError('Target outside workspace')

        d = np.clip(d, -1.0, 1.0)
        root = max(0.0, 1.0 - d**2)

        if elbow == 'down':
            q3 = np.arctan2(-np.sqrt(root), d)
        else:
            q3 = np.arctan2(np.sqrt(root), d)

        q2 = np.arctan2(zp, xp) - np.arctan2(
            self.l2 * np.sin(q3),
            self.l1 + self.l2 * np.cos(q3),
        )

        return np.array([q1, q2, q3], dtype=float)

    def fk_rrr(self, q):
        q1, q2, q3 = q

        xp = self.l1 * np.cos(q2) + self.l2 * np.cos(q2 + q3)
        zp = self.l1 * np.sin(q2) + self.l2 * np.sin(q2 + q3)

        x = xp * np.cos(q1)
        y = xp * np.sin(q1)
        z = zp

        return self.base_pos + np.array([x, y, z], dtype=float)

    def kinematic_to_motor(self, q_kin):
        return q_kin - self.q_offset

    def joint_positions(self, q):
        q1, q2, q3 = q

        ground = np.array([0.0, 0.0, 0.0])
        base = self.base_pos.copy()

        rz = np.array([
            [np.cos(q1), -np.sin(q1), 0.0],
            [np.sin(q1), np.cos(q1), 0.0],
            [0.0, 0.0, 1.0],
        ])

        xp1 = self.l1 * np.cos(q2)
        zp1 = self.l1 * np.sin(q2)
        elbow_local = np.array([xp1, 0.0, zp1])
        elbow = base + (rz @ elbow_local)

        xp2 = xp1 + self.l2 * np.cos(q2 + q3)
        zp2 = zp1 + self.l2 * np.sin(q2 + q3)
        wrist_local = np.array([xp2, 0.0, zp2])
        wrist = base + (rz @ wrist_local)

        return ground, base, elbow, wrist

    def target_callback(self, msg):
        self.target = np.array([msg.x, msg.y, msg.z], dtype=float)

    def _publish_joint_angles(self, q_motor):
        msg = Point32()
        msg.x = float(q_motor[0]) * 180.0 / np.pi
        msg.y = float(q_motor[1]) * 180.0 / np.pi
        msg.z = float(q_motor[2]) * 180.0 / np.pi
        self.joint_pub.publish(msg)

    def timer_callback(self):
        try:
            q_kin = self.ik_rrr_xyz(self.target, elbow=self.elbow_mode)
            q_motor = self.kinematic_to_motor(q_kin)
            self._publish_joint_angles(q_motor)

            self.last_q_motor = q_motor
            self.unreachable = False
        except ValueError:
            self.unreachable = True
            self.get_logger().warn('Target unreachable')

    def destroy_node(self):
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = Simulation()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()