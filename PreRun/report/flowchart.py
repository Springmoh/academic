"""
Robotic Arm ROS2 Coding Flowchart - direct viewer version

Usage:
    pip install pyflowchart
    python robotic_arm_flowchart_show_direct.py

What it does:
    1. Generates flowchart.js code using pyflowchart
    2. Saves the code as robotic_arm_flowchart_flowchartjs.txt
    3. Creates robotic_arm_flowchart.html
    4. Opens the HTML flowchart directly in your default browser

Note:
    The HTML viewer uses online flowchart.js libraries. If the browser page opens blank,
    make sure you are connected to the internet, or copy the generated .txt content into
    https://flowchart.js.org/
"""

from pathlib import Path
import webbrowser

try:
    from pyflowchart import StartNode, OperationNode, ConditionNode, EndNode, Flowchart
except ImportError:
    raise SystemExit("pyflowchart is not installed. Install it with: pip install pyflowchart")


# =========================
# Build pyflowchart nodes
# =========================
start = StartNode("Start ROS2 robotic arm system")
init = OperationNode("Initialize ROS2 nodes, YOLO model, camera, publishers, subscribers, QoS")
input_mode = ConditionNode("Input source?")

slider_input = OperationNode("Manual input: user adjusts x_t, y_t, z_t using slider GUI")
publish_slider = OperationNode("Publish target point to ROS2 topic")

camera_read = OperationNode("Read camera frame")
frame_ok = ConditionNode("Frame captured successfully?")
yolo_track = OperationNode("Run YOLO tracking on frame")
detection_ok = ConditionNode("Object detected with tracking ID?")

no_detection = OperationNode("No detection: publish default/home target and set z flag = 1")
process_boxes = OperationNode("For each detected box: calculate center, area, confidence, and track ID")
target_found = ConditionNode("Current target track ID found?")

center_check = ConditionNode("Target center inside tolerance area?")
publish_home = OperationNode("Publish home/center target coordinate")
publish_detected = OperationNode("Publish detected target center coordinate")

lost_check = ConditionNode("Target lost longer than timeout?")
retrack = OperationNode("Re-track target using nearest object or previous bounding region")
publish_results = OperationNode("Publish target coordinate, cut data, object count, and display annotated frame")

receive_target = OperationNode("Arm calculation node receives target point")
x_valid = ConditionNode("x_t > 0?")
fail_x = OperationNode("Reject target: x_t must be greater than 0")

calc_l_h_phi = OperationNode("Calculate l, h, and phi from target x_t, y_t, z_t")
reachable = ConditionNode("h <= 2 * arm_length?")
fail_reach = OperationNode("Reject target: point is outside reachable workspace")

calc_angles = OperationNode("Calculate theta, base angle a_b, elbow angle a_e, wrist angle a_w")
first_run = ConditionNode("First run?")
save_offset = OperationNode("Save initial angle offsets as home calibration")
publish_angles = OperationNode("Publish joint_angles in radians and stm32_angles in degrees")
loop = OperationNode("Loop while ROS2 is running")
end = EndNode("End / shutdown ROS2 nodes")

# =========================
# Connections
# =========================
start.connect(init)
init.connect(input_mode)

# Manual slider path
input_mode.connect_yes(slider_input, "Manual slider")
slider_input.connect(publish_slider)
publish_slider.connect(receive_target)

# Camera + YOLO path
input_mode.connect_no(camera_read, "Camera / YOLO")
camera_read.connect(frame_ok)
frame_ok.connect_no(end, "No")
frame_ok.connect_yes(yolo_track, "Yes")
yolo_track.connect(detection_ok)
detection_ok.connect_no(no_detection, "No")
no_detection.connect(publish_results)
detection_ok.connect_yes(process_boxes, "Yes")
process_boxes.connect(target_found)

target_found.connect_no(lost_check, "No")
target_found.connect_yes(center_check, "Yes")
center_check.connect_yes(publish_home, "Yes")
center_check.connect_no(publish_detected, "No")
publish_home.connect(lost_check)
publish_detected.connect(lost_check)

lost_check.connect_yes(retrack, "Yes")
lost_check.connect_no(publish_results, "No")
retrack.connect(publish_results)
publish_results.connect(receive_target)

# Arm calculation path
receive_target.connect(x_valid)
x_valid.connect_no(fail_x, "No")
fail_x.connect(loop)
x_valid.connect_yes(calc_l_h_phi, "Yes")
calc_l_h_phi.connect(reachable)
reachable.connect_no(fail_reach, "No")
fail_reach.connect(loop)
reachable.connect_yes(calc_angles, "Yes")
calc_angles.connect(first_run)
first_run.connect_yes(save_offset, "Yes")
first_run.connect_no(publish_angles, "No")
save_offset.connect(loop)
publish_angles.connect(loop)
loop.connect(camera_read)

# =========================
# Generate files and open viewer
# =========================
flowchart = Flowchart(start)
flowchart_code = flowchart.flowchart()

output_dir = Path(__file__).resolve().parent
txt_path = output_dir / "robotic_arm_flowchart_flowchartjs.txt"
html_path = output_dir / "robotic_arm_flowchart.html"

txt_path.write_text(flowchart_code, encoding="utf-8")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Robotic Arm ROS2 Coding Flowchart</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/raphael/2.3.0/raphael.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/flowchart/1.15.0/flowchart.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 24px;
            background: #f7f7f7;
        }}
        h1 {{
            font-size: 22px;
            margin-bottom: 6px;
        }}
        p {{
            margin-top: 0;
            color: #555;
        }}
        #diagram {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            overflow: auto;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
        }}
    </style>
</head>
<body>
    <h1>Robotic Arm ROS2 Coding Flowchart</h1>
    <p>Generated automatically from the Python pyflowchart script.</p>
    <div id="diagram"></div>

    <script>
        const code = `{flowchart_code.replace('`', '\\`')}`;
        const diagram = flowchart.parse(code);
        diagram.drawSVG('diagram', {{
            'line-width': 2,
            'font-size': 14,
            'font-family': 'Arial',
            'element-color': '#222',
            'line-color': '#222',
            'yes-text': 'Yes',
            'no-text': 'No',
            'flowstate': {{
                'default': {{ 'fill': '#ffffff' }}
            }}
        }});
    </script>
</body>
</html>
"""

html_path.write_text(html_content, encoding="utf-8")

print("Flowchart.js code saved to:", txt_path)
print("HTML flowchart saved to:", html_path)
print("Opening flowchart in your default browser...")
webbrowser.open(html_path.as_uri())
