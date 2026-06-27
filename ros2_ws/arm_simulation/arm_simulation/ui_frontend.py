import math
import threading
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from geometry_msgs.msg import Point32
from std_msgs.msg import Int16

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

from arm_simulation.home_config import HOME_POS, BASE_HEIGHT

# =========================
# Fixed variable
# =========================
La = 200.0   # mm


class UIFrontend(Node):
    def __init__(self):
        super().__init__('ui_frontend')

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.target_point_subscriber_ = self.create_subscription(
            Point32,
            "target_point",
            self.targetPointCallback,
            qos_profile
        )

        self.joint_angles_subscriber_ = self.create_subscription(
            Point32,
            "joint_angles",
            self.jointAnglesCallback,
            qos_profile
        )

        self.result_subscriber_ = self.create_subscription(
            Int16,
            "results",
            self.resultCallback,
            qos_profile
        )

        self.target_point_publisher_ = self.create_publisher(
            Point32,
            "target_point",
            qos_profile
        )

        

        # =========================
        # Manipulated variable
        # =========================
        self.x_t = 1.0
        self.y_t = 0.0
        self.z_t = 0.0

        # =========================
        # Output angle
        # =========================
        self.a_b = 0.0
        self.a_e = 0.0
        self.a_w = 0.0

        self.last_update_time = time.time()
        self.number_founded = None
        self.chili_history = []
        self.history_length = 200

    def resultCallback(self, msg):
        self.number_founded = int(msg.data)
        self.chili_history.append({
            "time": time.time(),
            "value": self.number_founded
        })
        if len(self.chili_history) > self.history_length:
            self.chili_history.pop(0)

    def targetPointCallback(self, msg):
        self.x_t = msg.x
        self.y_t = msg.y
        self.z_t = msg.z - BASE_HEIGHT
        self.last_update_time = time.time()

    def jointAnglesCallback(self, msg):
        self.a_b = msg.x
        self.a_e = msg.y
        self.a_w = msg.z
        self.last_update_time = time.time()

    def publish_target_point(self, x_t, y_t, z_t):
        msg = Point32()
        msg.x = float(x_t)
        msg.y = float(y_t)
        msg.z = float(z_t)
        self.target_point_publisher_.publish(msg)

    def get_state(self):
        x_t = self.x_t
        y_t = self.y_t
        z_t = self.z_t

        a_b = self.a_b
        a_e = self.a_e
        a_w = self.a_w

        # =========================
        # Plotting calculation only
        # =========================
        base_x = 0.0
        base_y = 0.0
        base_z = 0.0

        elbow_l = La * math.cos(a_e)
        elbow_z = La * math.sin(a_e)

        wrist_l = elbow_l + La * math.cos(a_w)
        wrist_z = elbow_z + La * math.sin(a_w)

        elbow_x = elbow_l * math.cos(a_b)
        elbow_y = elbow_l * math.sin(a_b)

        wrist_x = wrist_l * math.cos(a_b)
        wrist_y = wrist_l * math.sin(a_b)

        tolerance = 1e-3

        if (
            abs(wrist_x - x_t) < tolerance and
            abs(wrist_y - y_t) < tolerance and
            abs(wrist_z - z_t) < tolerance
        ):
            status = "PASS: wrist end = target point"
        else:
            status = "FAIL: wrist end != target point"

        return {
            "target": {
                "x_t": x_t,
                "y_t": y_t,
                "z_t": z_t
            },
            "angles": {
                "a_b": a_b,
                "a_e": a_e,
                "a_w": a_w,
                "a_b_deg": math.degrees(a_b),
                "a_e_deg": math.degrees(a_e),
                "a_w_deg": math.degrees(a_w)
            },
            "points": {
                "x": [base_x, elbow_x, wrist_x],
                "y": [base_y, elbow_y, wrist_y],
                "z": [base_z, elbow_z, wrist_z]
            },
            "wrist": {
                "wrist_x": wrist_x,
                "wrist_y": wrist_y,
                "wrist_z": wrist_z
            },
            "status": status,
            "last_update_time": self.last_update_time,
            "results": {
                "number_founded": self.number_founded,
                "history": self.chili_history
            }
        }


rclpy.init()
ui_frontend = UIFrontend()

app = FastAPI()


def ros_spin_thread():
    rclpy.spin(ui_frontend)


threading.Thread(target=ros_spin_thread, daemon=True).start()


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>3DOF Robotic Arm Web Plot</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f7f7f7;
        }

        h2 {
            margin-bottom: 5px;
        }

        .container {
            display: flex;
            gap: 20px;
        }

        #plot {
            width: 75vw;
            height: 80vh;
            background: white;
            border-radius: 10px;
        }

        .panel {
            width: 300px;
            background: white;
            padding: 15px;
            border-radius: 10px;
        }

        .row {
            margin-bottom: 12px;
        }

        label {
            display: block;
            font-weight: bold;
        }

        input[type=range] {
            width: 100%;
        }

        .value {
            font-family: monospace;
        }

        #status {
            font-weight: bold;
            margin-top: 10px;
        }

        #history_plot {
            width: 100%;
            height: 220px;
            margin-top: 15px;
        }

        button {
            width: 100%;
            padding: 8px;
            margin-top: 8px;
        }
    </style>
</head>
<body>
    <h2>3DOF Robotic Arm Web Plot</h2>
    <p>FastAPI + Uvicorn + ROS 2 topic subscriber</p>

    <div class="container">
        <div id="plot"></div>

        <div class="panel">
            <h3>Target point</h3>

            <div class="row">
                <label>x_t / mm: <span id="x_val" class="value">150</span></label>
                <input id="x_t" type="range" min="-200" max="400" value="150" step="1">
            </div>

            <div class="row">
                <label>y_t / mm: <span id="y_val" class="value">100</span></label>
                <input id="y_t" type="range" min="-400" max="400" value="100" step="1">
            </div>

            <div class="row">
                <label>z_t / mm: <span id="z_val" class="value">120</span></label>
                <input id="z_t" type="range" min="-450" max="450" value="120" step="1">
            </div>

            <button onclick="sendTarget()">Publish target_point</button>

            <h3>Joint angles</h3>
            <pre id="info"></pre>

            <div id="status"></div>

            <div id="chili_detection">
                <h3>Chili detection</h3>
                <div class="row">
                    <label>Detected chili count:</label>
                    <div id="chili_value" class="value">-</div>
                </div>
                <div id="history_plot"></div>
            </div>
        </div>
    </div>

<script>
let layout = {
    scene: {
        xaxis: {title: "X / mm", range: [-200, 450]},
        yaxis: {title: "Y / mm", range: [-450, 450]},
        zaxis: {title: "Z / mm", range: [-450, 450]},
        aspectmode: "cube"
    },
    margin: {l: 0, r: 0, b: 0, t: 30},
    title: "3DOF Robotic Arm"
};

let armTrace = {
    x: [0, 0, 0],
    y: [0, 0, 0],
    z: [0, 0, 0],
    mode: "lines+markers",
    type: "scatter3d",
    name: "Arm",
    line: {width: 8},
    marker: {size: 6}
};

let targetTrace = {
    x: [150],
    y: [100],
    z: [120],
    mode: "markers",
    type: "scatter3d",
    name: "Target",
    marker: {size: 6, symbol: "x"}
};

Plotly.newPlot("plot", [armTrace, targetTrace], layout);

function updateSliderLabels() {
    document.getElementById("x_val").innerText = document.getElementById("x_t").value;
    document.getElementById("y_val").innerText = document.getElementById("y_t").value;
    document.getElementById("z_val").innerText = document.getElementById("z_t").value;
}

document.getElementById("x_t").oninput = updateSliderLabels;
document.getElementById("y_t").oninput = updateSliderLabels;
document.getElementById("z_t").oninput = updateSliderLabels;

async function sendTarget() {
    updateSliderLabels();

    let x_t = parseFloat(document.getElementById("x_t").value);
    let y_t = parseFloat(document.getElementById("y_t").value);
    let z_t = parseFloat(document.getElementById("z_t").value);

    await fetch("/target", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            x_t: x_t,
            y_t: y_t,
            z_t: z_t
        })
    });
}

async function updatePlot() {
    let response = await fetch("/state");
    let data = await response.json();

    Plotly.update("plot", {
        x: [data.points.x, [data.target.x_t]],
        y: [data.points.y, [data.target.y_t]],
        z: [data.points.z, [data.target.z_t]]
    });

    document.getElementById("info").innerText =
        "a_b = " + data.angles.a_b.toFixed(4) + " rad / " + data.angles.a_b_deg.toFixed(2) + " deg\\n" +
        "a_e = " + data.angles.a_e.toFixed(4) + " rad / " + data.angles.a_e_deg.toFixed(2) + " deg\\n" +
        "a_w = " + data.angles.a_w.toFixed(4) + " rad / " + data.angles.a_w_deg.toFixed(2) + " deg\\n\\n" +
        "wrist_x = " + data.wrist.wrist_x.toFixed(2) + " mm\\n" +
        "wrist_y = " + data.wrist.wrist_y.toFixed(2) + " mm\\n" +
        "wrist_z = " + data.wrist.wrist_z.toFixed(2) + " mm\\n\\n" +
        "x_t = " + data.target.x_t.toFixed(2) + " mm\\n" +
        "y_t = " + data.target.y_t.toFixed(2) + " mm\\n" +
        "z_t = " + data.target.z_t.toFixed(2) + " mm";

    document.getElementById("status").innerText = data.status;
    document.getElementById("chili_value").innerText = data.results.number_founded !== null ? data.results.number_founded : "-";

    let history = data.results.history || [];
    let historyX = history.map(item => new Date(item.time * 1000));
    let historyY = history.map(item => item.value);

    Plotly.react("history_plot", [{
        x: historyX,
        y: historyY,
        mode: "lines+markers",
        name: "Chili count",
        line: {shape: "hv", width: 2},
        marker: {size: 6}
    }], {
        margin: {l: 40, r: 10, b: 30, t: 30},
        xaxis: {title: "Time"},
        yaxis: {title: "Number found", rangemode: "tozero"},
        showlegend: false
    }, {displayModeBar: false});
}

setInterval(updatePlot, 1000);
sendTarget();
</script>
</body>
</html>
"""


@app.get("/state")
def get_state():
    return JSONResponse(ui_frontend.get_state())


@app.post("/target")
async def set_target(data: dict):
    x_t = data.get("x_t", 1.0)
    y_t = data.get("y_t", 0.0)
    z_t = data.get("z_t", 0.0)

    ui_frontend.publish_target_point(x_t, y_t, z_t)

    return {
        "published": True,
        "x_t": x_t,
        "y_t": y_t,
        "z_t": z_t
    }


def main(args=None):
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()