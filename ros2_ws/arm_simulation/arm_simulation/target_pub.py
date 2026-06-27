import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from geometry_msgs.msg import Point32

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

from arm_simulation.home_config import HOME_POS


class TargetPointSlider(Node):
    def __init__(self):
        super().__init__("target_point_slider")

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.target_point_publisher_ = self.create_publisher(
            Point32,
            "target_request",
            qos_profile
        )

        self.x_t = HOME_POS[0]
        self.y_t = HOME_POS[1]
        self.z_t = HOME_POS[2]

        self.get_logger().info("Target point slider started!")

    def publish_target_point(self):
        msg = Point32()
        msg.x = float(self.x_t)
        msg.y = float(self.y_t)
        msg.z = float(self.z_t)

        self.target_point_publisher_.publish(msg)

        self.get_logger().info(
            f"Published target_point: "
            f"x={self.x_t:.2f}, y={self.y_t:.2f}, z={self.z_t:.2f}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = TargetPointSlider()

    fig, ax = plt.subplots(figsize=(8, 5))
    plt.subplots_adjust(left=0.15, bottom=0.35)

    ax.set_title("Target Point Publisher")
    ax.axis("off")

    text_info = ax.text(
        0.1,
        0.6,
        "",
        fontsize=12,
        transform=ax.transAxes
    )

    # =========================
    # Slider setup
    # =========================
    ax_x_t = plt.axes([0.15, 0.22, 0.70, 0.03])
    ax_y_t = plt.axes([0.15, 0.16, 0.70, 0.03])
    ax_z_t = plt.axes([0.15, 0.10, 0.70, 0.03])

    slider_x_t = Slider(
        ax_x_t,
        "x_t / mm",
        -200.0,
        400.0,
        valinit=node.x_t
    )

    slider_y_t = Slider(
        ax_y_t,
        "y_t / mm",
        -400.0,
        400.0,
        valinit=node.y_t
    )

    slider_z_t = Slider(
        ax_z_t,
        "z_t / mm",
        -450.0,
        450.0,
        valinit=node.z_t
    )

    def update(val):
        node.x_t = slider_x_t.val
        node.y_t = slider_y_t.val
        node.z_t = slider_z_t.val

        node.publish_target_point()

        text_info.set_text(
            f"Publishing to /target_point\n\n"
            f"x_t = {node.x_t:.2f} mm\n"
            f"y_t = {node.y_t:.2f} mm\n"
            f"z_t = {node.z_t:.2f} mm"
        )

        rclpy.spin_once(node, timeout_sec=0.001)
        fig.canvas.draw_idle()

    slider_x_t.on_changed(update)
    slider_y_t.on_changed(update)
    slider_z_t.on_changed(update)

    update(None)

    try:
        plt.show()
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()