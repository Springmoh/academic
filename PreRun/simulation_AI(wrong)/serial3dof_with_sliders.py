#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons

# 3‑DOF Serial Arm (Yaw‑Pitch‑Pitch) — Interactive Sliders for X, Y, Z
# ---------------------------------------------------------------
# Adjust the target Cartesian position with sliders and watch the arm move.
# Uses analytic IK (elbow-up/down selectable via radio buttons).
#
# Joints:
#   q1: yaw about +Z
#   q2: shoulder pitch
#   q3: elbow pitch
#
# Geometry (edit as needed): base -- elbow -- wrist
L1 = 200.0  # shoulder->elbow (mm)
L2 = 200.0  # elbow->wrist  (mm)
BASE_POS = np.array([0.0, 0.0, 165.0])  # shoulder/base joint position in world frame
# ---------- Motor zero offset ----------
HOME_POS = np.array([150.0, 0.0, 215.0])   # when motor angle = [0,0,0]

# ---------- IK and FK ----------
def ik_rrr_xyz(p, elbow="down"):
    # Convert world target position into arm-local coordinates
    p_local = np.array(p, dtype=float) - BASE_POS

    x, y, z = float(p_local[0]), float(p_local[1]), float(p_local[2])
    q1 = np.arctan2(y, x)
    r = np.hypot(x, y)
    xp, zp = r, z

    D = (xp**2 + zp**2 - L1**2 - L2**2) / (2.0 * L1 * L2)

    eps = 1e-6
    if D < -1.0 - eps or D > 1.0 + eps:
        print("TNF p =", p, "D =", D)
        raise ValueError("Target outside workspace")

    D = np.clip(D, -1.0, 1.0)

    root = max(0.0, 1.0 - D**2)

    if elbow == "down":
        q3 = np.arctan2(-np.sqrt(root), D)
    else:
        q3 = np.arctan2(+np.sqrt(root), D)

    q2 = np.arctan2(zp, xp) - np.arctan2(
        L2*np.sin(q3),
        L1 + L2*np.cos(q3)
    )

    return np.array([q1, q2, q3])

def fk_rrr(q):
    q1, q2, q3 = q

    xp = L1*np.cos(q2) + L2*np.cos(q2 + q3)
    zp = L1*np.sin(q2) + L2*np.sin(q2 + q3)

    x = xp*np.cos(q1)
    y = xp*np.sin(q1)
    z = zp

    # Convert from arm-local coordinates back to world coordinates
    return BASE_POS + np.array([x, y, z])



# This is the actual mathematical joint angle needed to reach HOME_POS
q_offset = ik_rrr_xyz(HOME_POS, elbow="down")

def motor_to_kinematic(q_motor):
    """
    Convert motor angle to real kinematic joint angle.
    Motor angle [0,0,0] means robot is at HOME_POS.
    """
    return q_motor + q_offset

def kinematic_to_motor(q_kin):
    """
    Convert real kinematic joint angle to motor angle.
    """
    return q_kin - q_offset

def fk_motor(q_motor):
    """
    FK using motor angles.
    """
    q_kin = motor_to_kinematic(q_motor)
    return fk_rrr(q_kin)

def joint_positions(q):
    q1, q2, q3 = q

    ground = np.array([0.0, 0.0, 0.0])
    base = BASE_POS.copy()

    # Rotation about Z for the yaw
    Rz = np.array([[np.cos(q1), -np.sin(q1), 0.0],
                   [np.sin(q1),  np.cos(q1), 0.0],
                   [0.0,         0.0,        1.0]])

    # Shoulder -> Elbow in local arm plane
    xp1 = L1*np.cos(q2)
    zp1 = L1*np.sin(q2)
    elbow_local = np.array([xp1, 0.0, zp1])
    elbow = base + (Rz @ elbow_local)

    # Elbow -> Wrist in local arm plane
    xp2 = xp1 + L2*np.cos(q2 + q3)
    zp2 = zp1 + L2*np.sin(q2 + q3)
    wrist_local = np.array([xp2, 0.0, zp2])
    wrist = base + (Rz @ wrist_local)

    return ground, base, elbow, wrist

# ---------- Plot setup ----------
reach = L1 + L2
lim = reach * 1.05

fig = plt.figure(figsize=(8, 7))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(left=0.1, bottom=0.22, right=0.88)

# Initial target
q_motor0 = np.array([0.0, 0.0, 0.0])
p = fk_motor(q_motor0)
elbow_mode = {"mode": "down"}

# Plot elements (placeholders)
arm_line, = ax.plot([], [], [], marker='o')
target_scatter = ax.scatter([], [], [])
txt1 = ax.text2D(0.02, 0.95, "", transform=ax.transAxes)
txt2 = ax.text2D(0.02, 0.90, "", transform=ax.transAxes)
status_txt = ax.text2D(0.55, 0.95, "", transform=ax.transAxes)

def draw_arm(q, target=None):
    ground, base, elbow, wrist = joint_positions(q)
    pts = np.vstack([ground, base, elbow, wrist])
    arm_line.set_data(pts[:,0], pts[:,1])
    arm_line.set_3d_properties(pts[:,2])

    if target is not None:
        target_scatter._offsets3d = ([target[0]],[target[1]],[target[2]])

    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(0, BASE_POS[2] + reach)
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title('3‑DOF Serial Arm — IK with X/Y/Z Sliders')

def update_plot(val=None):
    x = s_x.val
    y = s_y.val
    z = s_z.val
    p[:] = [x, y, z]
    try:
        q_kin = ik_rrr_xyz(p, elbow=elbow_mode["mode"])
        q_motor = kinematic_to_motor(q_kin)
        print("target =", p)
        print("q_kin deg   =", np.rad2deg(q_kin))
        print("q_motor deg =", np.rad2deg(q_motor))
        print("q_offset deg=", np.rad2deg(q_offset))
        print("FK check =", fk_rrr(q_kin))

        ee = fk_rrr(q_kin)
        draw_arm(q_kin, target=p)

        txt1.set_text("motor q (deg) = [{:.1f}, {:.1f}, {:.1f}]".format(*np.rad2deg(q_motor)))
        status_txt.set_text("")
    except ValueError as e:
        # Outside workspace: clear arm line to base only
        base = np.array([0.0,0.0,0.0])
        arm_line.set_data([0,0],[0,0])
        arm_line.set_3d_properties([0,0])
        target_scatter._offsets3d = ([p[0]],[p[1]],[p[2]])
        txt1.set_text("")
        txt2.set_text("")
        status_txt.set_text("Unreachable target")

    fig.canvas.draw_idle()

# ---------- Sliders ----------
ax_x = plt.axes([0.10, 0.12, 0.65, 0.03])
ax_y = plt.axes([0.10, 0.08, 0.65, 0.03])
ax_z = plt.axes([0.10, 0.04, 0.65, 0.03])

s_x = Slider(ax_x, 'X (mm)', -lim, lim, valinit=p[0], valstep=1.0)
s_y = Slider(ax_y, 'Y (mm)', -lim, lim, valinit=p[1], valstep=1.0)
s_z = Slider(ax_z,'Z (mm)',0,BASE_POS[2] + reach,valinit=p[2],valstep=1.0)

s_x.on_changed(update_plot)
s_y.on_changed(update_plot)
s_z.on_changed(update_plot)

# ---------- Elbow mode radio ----------
rax = plt.axes([0.90, 0.55, 0.08, 0.12])
radio = RadioButtons(rax, ('down', 'up'))
radio.set_active(0)

def elbow_changed(label):
    elbow_mode["mode"] = label
    update_plot()

radio.on_clicked(elbow_changed)

# Initial draw
update_plot()
plt.show()
