"""
2.7 System Flow Chart - ROS2 Robotic Arm Harvesting System

Run:
    python robotic_arm_system_flow_chart_direct.py

Required:
    sudo apt install graphviz        # Linux, if 'dot' command is missing
    pip install matplotlib pillow    # only needed for direct preview

Output:
    robotic_arm_system_flow_chart.png
    robotic_arm_system_flow_chart.pdf
    robotic_arm_system_flow_chart.dot

The script saves the flow chart and displays it directly after running.
"""

from pathlib import Path
import shutil
import subprocess

OUT_DIR = Path(__file__).resolve().parent
DOT_PATH = OUT_DIR / "robotic_arm_system_flow_chart.dot"
PNG_PATH = OUT_DIR / "robotic_arm_system_flow_chart.png"
PDF_PATH = OUT_DIR / "robotic_arm_system_flow_chart.pdf"

DOT = r'''
digraph SystemFlowChart {
    graph [
        rankdir=TB,
        bgcolor="white",
        pad="0.30",
        nodesep="0.45",
        ranksep="0.55",
        splines=ortho,
        fontname="Arial",
        labelloc="t",
        label="2.7 System Flow Chart - ROS2 Robotic Arm Harvesting System\nOverall process integrating inputs, processing, outputs, and feedback loops"
    ];

    node [
        shape=rect,
        style="rounded",
        fontname="Arial",
        fontsize=11,
        margin="0.13,0.09",
        width=2.2,
        height=0.55,
        color="black"
    ];

    edge [
        fontname="Arial",
        fontsize=10,
        arrowsize=0.75,
        color="black"
    ];

    start [shape=oval, style="rounded,bold", label="START"];
    init [label="Initialize ROS2 system\n- Load YOLO model / home position\n- Set QoS\n- Create publishers and subscribers"];
    input [shape=diamond, width=3.2, height=1.0, label="Input source?"];

    camera [label="Camera captures frame\nfrom USB camera"];
    yolo [label="YOLO vision processing\nDetect object, bounding box, Track ID"];
    detected [shape=diamond, width=3.0, height=1.0, label="Object detected?"];
    lost [label="Target not found\nReturn to home/tolerance point\nSet lost flag and retry"];
    tracking [label="Target tracking and selection\n- Select target Track ID\n- Calculate center and area\n- Apply tolerance region"];

    manual [label="Manual user input\nSlider / web UI sets X, Y, Z target"];
    calibration [label="Use manual target\nfor testing or calibration"];

    publish_target [label="Publish target coordinate\nROS2 topic: /target_point or /target_coordinate"];
    ik [label="Arm calculation node\nCompute inverse kinematics\nOutput: a_b, a_e, a_w"];
    reachable [shape=diamond, width=3.0, height=1.0, label="Target reachable?\nx_t > 0 and h <= 2L"];
    unreachable [label="Unreachable target\nWarn user / ignore command\nRequest a new target"];
    publish_angles [label="Publish joint angles\nROS2 topics: /joint_angles and /stm32_angles"];
    controller [label="STM32 / motor controller\nConvert angle data to motor commands"];
    actuator [label="Robotic arm movement\nBase, elbow, wrist and cutter move to target"];
    feedback [label="Feedback and monitoring\nUI displays target, angles, detection count, status"];
    cont [shape=diamond, width=3.0, height=1.0, label="Continue operation?"];
    end [shape=oval, style="rounded,bold", label="END"];

    note [
        shape=note,
        label="Data flow summary:\l1. Input: camera detection or manual target point.\l2. Processing: YOLO tracking, target selection, inverse kinematics.\l3. Output: joint angles and STM32 motor commands.\l4. Feedback: UI status, detection count, reachability warnings, repeated loop.\l"
    ];

    start -> init;
    init -> input;

    input -> camera [label="Auto mode"];
    camera -> yolo;
    yolo -> detected;
    detected -> tracking [label="Yes"];
    detected -> lost [label="No"];
    lost -> camera [label="Retry"];
    tracking -> publish_target;

    input -> manual [label="Manual mode"];
    manual -> calibration;
    calibration -> publish_target;

    publish_target -> ik;
    ik -> reachable;
    reachable -> publish_angles [label="Yes"];
    reachable -> unreachable [label="No"];
    unreachable -> input [label="New target"];

    publish_angles -> controller;
    controller -> actuator;
    actuator -> feedback;
    feedback -> cont;
    cont -> input [label="Yes / loop"];
    cont -> end [label="No"];
    end -> note [style=invis];
}
'''


def render_graph():
    DOT_PATH.write_text(DOT, encoding="utf-8")

    dot_cmd = shutil.which("dot")
    if dot_cmd is None:
        raise RuntimeError("Graphviz 'dot' command not found. Install Graphviz first.")

    subprocess.run([dot_cmd, "-Tpng", str(DOT_PATH), "-o", str(PNG_PATH)], check=True)
    subprocess.run([dot_cmd, "-Tpdf", str(DOT_PATH), "-o", str(PDF_PATH)], check=True)

    print(f"Saved: {PNG_PATH}")
    print(f"Saved: {PDF_PATH}")
    print(f"Saved: {DOT_PATH}")


def show_image():
    try:
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        img = mpimg.imread(PNG_PATH)
        plt.figure(figsize=(11, 15))
        plt.imshow(img)
        plt.axis("off")
        plt.tight_layout()
        plt.show()
    except Exception as exc:
        print("Preview skipped:", exc)
        print("Open the PNG file manually to view the flow chart.")


if __name__ == "__main__":
    render_graph()
    show_image()
