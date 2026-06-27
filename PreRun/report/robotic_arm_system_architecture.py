"""
Robotic Arm ROS2 System Architecture Block Diagram
Run this script to save and directly show the architecture diagram.

Usage:
    python robotic_arm_system_architecture.py

Output:
    robotic_arm_system_architecture.png
    robotic_arm_system_architecture.pdf
"""

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT_DIR = Path(__file__).resolve().parent
PNG_PATH = OUT_DIR / "robotic_arm_system_architecture.png"
PDF_PATH = OUT_DIR / "robotic_arm_system_architecture.pdf"


def add_box(ax, xy, w, h, title, body="", fontsize=10):
    x, y = xy
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.025,rounding_size=0.04",
        linewidth=1.6,
        facecolor="white",
        edgecolor="black",
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h - 0.10, title, ha="center", va="top", fontsize=fontsize, fontweight="bold")
    if body:
        ax.text(x + w / 2, y + h / 2 - 0.03, body, ha="center", va="center", fontsize=fontsize - 1)
    return box


def add_arrow(ax, start, end, label="", curve=0.0, fontsize=8):
    arrow = FancyArrowPatch(
        start, end,
        arrowstyle="-|>",
        mutation_scale=14,
        linewidth=1.35,
        color="black",
        connectionstyle=f"arc3,rad={curve}",
        shrinkA=4,
        shrinkB=4,
    )
    ax.add_patch(arrow)
    if label:
        mx = (start[0] + end[0]) / 2
        my = (start[1] + end[1]) / 2
        ax.text(mx, my + 0.08, label, ha="center", va="center", fontsize=fontsize,
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="none"))


def main():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(
        7, 7.65,
        "Robotic Arm ROS2 System Architecture / Block Diagram",
        ha="center", va="center", fontsize=16, fontweight="bold"
    )
    ax.text(
        7, 7.32,
        "Overview of sensor input, processing, ROS2 communication, kinematic calculation, actuator output, and user interface",
        ha="center", va="center", fontsize=10
    )

    # Input layer
    add_box(ax, (0.6, 5.85), 2.15, 0.95, "Camera Sensor", "/dev/video4\nLive image frames")
    add_box(ax, (0.6, 4.35), 2.15, 0.95, "User Interface", "FastAPI / Web UI\nManual x, y, z input")
    add_box(ax, (0.6, 2.85), 2.15, 0.95, "Slider Publisher", "target_pub.py\nTest target point")
    add_box(ax, (0.6, 1.35), 2.15, 0.95, "Arm Feedback", "current_coordinates\nActual arm position")

    # Processing layer
    add_box(ax, (3.45, 5.60), 2.5, 1.45, "Vision Processing Node", "image_processing.py\nOpenCV + YOLO tracking\nFind target object")
    add_box(ax, (3.45, 2.85), 2.5, 1.30, "PID / Target Planner", "pid_calc.cpp\nConvert camera target\ninto robot target point")

    # ROS topics layer
    add_box(ax, (6.65, 6.00), 2.0, 0.70, "ROS2 Topic", "target_coordinate")
    add_box(ax, (6.65, 5.05), 2.0, 0.70, "ROS2 Topic", "cutdata / results")
    add_box(ax, (6.65, 3.55), 2.0, 0.70, "ROS2 Topic", "target_point")
    add_box(ax, (6.65, 2.55), 2.0, 0.70, "ROS2 Topic", "cut_request")

    # Calculation layer
    add_box(ax, (9.45, 4.85), 2.55, 1.35, "Arm Calculation Node", "angle_calc.cpp or\nsimulation.py\nInverse kinematics")
    add_box(ax, (9.45, 3.05), 2.55, 1.10, "Reachability Check", "Check workspace limit\nReject invalid target")

    # Output layer
    add_box(ax, (12.45, 5.05), 1.9, 0.95, "Joint Angles", "joint_angles\na_b, a_e, a_w")
    add_box(ax, (12.45, 3.70), 1.9, 0.95, "STM32 Output", "stm32_angles\nMotor commands")
    add_box(ax, (12.45, 2.20), 1.9, 0.95, "Actuators", "Base, elbow, wrist\nCutter mechanism")
    add_box(ax, (9.45, 1.35), 2.55, 0.90, "Display / Monitoring", "Annotated video\nWeb status / logs")

    # Arrows - main flow
    add_arrow(ax, (2.75, 6.32), (3.45, 6.32), "frames")
    add_arrow(ax, (5.95, 6.45), (6.65, 6.35), "Point x,y,z")
    add_arrow(ax, (5.95, 5.80), (6.65, 5.40), "cut/result")
    add_arrow(ax, (8.65, 6.35), (9.45, 5.78), "target data", curve=-0.10)
    add_arrow(ax, (8.65, 5.38), (9.45, 1.95), "status")

    # UI/manual input flows
    add_arrow(ax, (2.75, 4.82), (6.65, 3.90), "manual target")
    add_arrow(ax, (2.75, 3.32), (6.65, 3.90), "test target")
    add_arrow(ax, (8.65, 3.90), (9.45, 5.25), "Point32 x,y,z", curve=-0.12)
    add_arrow(ax, (2.75, 1.82), (3.45, 3.25), "feedback")
    add_arrow(ax, (8.65, 2.90), (12.45, 2.68), "cutter command")

    # Planner path
    add_arrow(ax, (6.65, 6.20), (5.95, 3.52), "target_coordinate", curve=0.12)
    add_arrow(ax, (5.95, 3.50), (6.65, 3.90), "planned point")

    # Calculation output
    add_arrow(ax, (10.70, 4.85), (10.70, 4.15), "workspace test")
    add_arrow(ax, (12.00, 5.55), (12.45, 5.52), "publish")
    add_arrow(ax, (12.00, 4.00), (12.45, 4.18), "degree offset")
    add_arrow(ax, (13.40, 3.70), (13.40, 3.15), "drive motors")
    add_arrow(ax, (12.45, 5.40), (9.45, 1.88), "visualize angles", curve=0.15)

    # Footer notes
    ax.text(
        7, 0.55,
        "Communication layer: ROS2 publishers/subscribers with best-effort QoS. Main data types: geometry_msgs/Point, geometry_msgs/Point32, std_msgs/Int16, std_msgs/Bool.",
        ha="center", va="center", fontsize=9
    )

    plt.tight_layout()
    fig.savefig(PNG_PATH, dpi=200, bbox_inches="tight")
    fig.savefig(PDF_PATH, bbox_inches="tight")
    print(f"Saved: {PNG_PATH}")
    print(f"Saved: {PDF_PATH}")
    plt.show()


if __name__ == "__main__":
    main()
