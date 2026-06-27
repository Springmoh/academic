import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# =========================
# Fixed variable
# =========================
La = 200.0   # mm

# =========================
# Initial manipulated variable
# =========================
x_t = 150.0
y_t = 0.0
z_t = 120.0

# =========================
# Matplotlib setup
# =========================
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

plt.subplots_adjust(left=0.1, bottom=0.30)

ax.set_xlim(-300, 450)
ax.set_ylim(-450, 450)
ax.set_zlim(-100, 450)

ax.set_xlabel("X / mm")
ax.set_ylabel("Y / mm")
ax.set_zlabel("Z / mm")
ax.set_title("3DOF Robotic Arm Simulation")

arm_line, = ax.plot([], [], [], 'o-', linewidth=3)
target_point, = ax.plot([], [], [], 'x', markersize=10)
wrist_point, = ax.plot([], [], [], 'o', markersize=8)

text_info = ax.text2D(0.02, 0.95, "", transform=ax.transAxes)
status_text = ax.text2D(0.02, 0.05, "", transform=ax.transAxes)


def calculate_and_plot():
    global x_t, y_t, z_t
    global l, h, phi, theta
    global ab, ae, aw

    try:
        # =========================
        # Your final algorithm
        # Do not change this part
        # =========================
        l = np.sqrt(x_t**2 + y_t**2)
        h = np.sqrt(z_t**2 + x_t**2 + y_t**2)
        phi = np.arctan(z_t / l)
        theta = np.arccos(h / (2 * La))

        ab = np.arctan(y_t / x_t)
        ae = phi + theta
        aw = phi - theta

        # =========================
        # Plotting only
        # =========================
        base_x = 0
        base_y = 0
        base_z = 0

        elbow_l = La * np.cos(ae)
        elbow_z = La * np.sin(ae)

        wrist_l = elbow_l + La * np.cos(aw)
        wrist_z = elbow_z + La * np.sin(aw)

        elbow_x = elbow_l * np.cos(ab)
        elbow_y = elbow_l * np.sin(ab)

        wrist_x = wrist_l * np.cos(ab)
        wrist_y = wrist_l * np.sin(ab)

        x_data = [base_x, elbow_x, wrist_x]
        y_data = [base_y, elbow_y, wrist_y]
        z_data = [base_z, elbow_z, wrist_z]

        arm_line.set_data(x_data, y_data)
        arm_line.set_3d_properties(z_data)

        target_point.set_data([x_t], [y_t])
        target_point.set_3d_properties([z_t])

        wrist_point.set_data([wrist_x], [wrist_y])
        wrist_point.set_3d_properties([wrist_z])

        # =========================
        # Verification
        # =========================
        tolerance = 1e-6

        if (
            abs(wrist_x - x_t) < tolerance and
            abs(wrist_y - y_t) < tolerance and
            abs(wrist_z - z_t) < tolerance
        ):
            status = "PASS: wrist end = target point"
        else:
            status = "FAIL: wrist end != target point"
            print("FAIL")

        text_info.set_text(
            f"x_t = {x_t:.2f} mm, y_t = {y_t:.2f} mm, z_t = {z_t:.2f} mm\n"
            f"l = {l:.2f} mm, h = {h:.2f} mm\n"
            f"phi = {np.degrees(phi):.2f} deg\n"
            f"theta = {np.degrees(theta):.2f} deg\n"
            f"ab = {np.degrees(ab):.2f} deg\n"
            f"ae = {np.degrees(ae):.2f} deg\n"
            f"aw = {np.degrees(aw):.2f} deg\n\n"
            f"wrist_x = {wrist_x:.2f} mm\n"
            f"wrist_y = {wrist_y:.2f} mm\n"
            f"wrist_z = {wrist_z:.2f} mm"
        )

        status_text.set_text(status)

    except:
        arm_line.set_data([], [])
        arm_line.set_3d_properties([])

        target_point.set_data([x_t], [y_t])
        target_point.set_3d_properties([z_t])

        wrist_point.set_data([], [])
        wrist_point.set_3d_properties([])

        text_info.set_text(
            f"x_t = {x_t:.2f} mm, y_t = {y_t:.2f} mm, z_t = {z_t:.2f} mm\n"
            f"Calculation error"
        )

        status_text.set_text("FAIL: invalid target point")
        print("FAIL")

    fig.canvas.draw_idle()


# =========================
# Slider setup
# =========================
ax_x_t = plt.axes([0.15, 0.20, 0.70, 0.03])
ax_y_t = plt.axes([0.15, 0.15, 0.70, 0.03])
ax_z_t = plt.axes([0.15, 0.10, 0.70, 0.03])

slider_x_t = Slider(ax_x_t, "x_t / mm", 1.0, 400.0, valinit=x_t)
slider_y_t = Slider(ax_y_t, "y_t / mm", -400.0, 400.0, valinit=y_t)
slider_z_t = Slider(ax_z_t, "z_t / mm", -450.0, 450.0, valinit=z_t)


def update(val):
    global x_t, y_t, z_t

    x_t = slider_x_t.val
    y_t = slider_y_t.val
    z_t = slider_z_t.val

    calculate_and_plot()


slider_x_t.on_changed(update)
slider_y_t.on_changed(update)
slider_z_t.on_changed(update)

calculate_and_plot()

plt.show()