# arm_simulation

`arm_simulation` is a ROS 2 Python package for an arm control and vision demo. It provides nodes for target publishing, simulation, a FastAPI-based UI frontend, and YOLO-based image processing.

## Included nodes

- `target_pub` - publishes target data for the arm workflow
- `simulation` - runs the arm simulation logic
- `ui_frontend` - starts the web frontend/API layer
- `image_processing` - runs YOLO inference on live camera frames and displays annotated output

## Requirements

- ROS 2 environment with `colcon`
- Python dependencies used by the package, including `rclpy`, `opencv-python`, `fastapi`, `uvicorn`, and `ultralytics`
- A YOLO model file named `yolo26n.pt`
- A camera device available at `/dev/video4` for the image processing node

If you are missing system Python dependencies, install them with `rosdep` from the workspace root:

```bash
rosdep install --from-paths src --ignore-src -y
```

If pip reports an externally managed environment error on Linux, use:

```bash
PIP_BREAK_SYSTEM_PACKAGES=1 rosdep install --from-paths src --ignore-src -y
```

## Build

From the workspace root:

```bash
colcon build --symlink-install
source install/setup.bash
```

## Run

After sourcing the workspace, launch any node with `ros2 run`:

```bash
ros2 run arm_simulation target_pub
ros2 run arm_simulation simulation
ros2 run arm_simulation ui_frontend
ros2 run arm_simulation image_processing
```

## Image processing notes

The image processing node opens `/dev/video4`, configures the camera for MJPG at 640x360 and 60 FPS, and runs YOLO inference on each frame. Press `q` in the display window to exit.

The current code loads the model with a relative path:

```python
YOLO("yolo26n.pt")
```

If sometime the performance is lag, you might need to change the format of the video to MJPEG
```
ffplay -f v4l2 -input_format mjpeg -video_size 640x480 -framerate 30 /dev/video0
```

That means the model file must be available from the working directory used to start the node, or the path in `image_processing.py` should be updated to an absolute path.

## Package layout

- `arm_simulation/image_processing.py` - camera capture and YOLO inference
- `arm_simulation/simulation.py` - simulation entry point
- `arm_simulation/target_pub.py` - target publishing entry point
- `arm_simulation/ui_frontend.py` - FastAPI/uvicorn frontend entry point
- `arm_simulation/reference/` - reference assets and example media
