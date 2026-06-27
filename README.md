# IDP_sharing

This repository contains a robotics research/demo workspace with ROS 2 simulation and supporting pre-run experiment scripts.

## Repository layout

- `PreRun/`
  - `image_processing/` - scripts for recording video, extracting frames, and renaming files
  - `report/` - flowchart scripts and generated flowchart HTML
  - `simulation_AI(wrong)/` - earlier exploration of an AI simulation interface
  - `simulation_mohnc/` - a local simulation script

- `ros2_ws/`
  - `arm_calculation/` - ROS 2 C++ package for arm angle and PID calculations
  - `arm_simulation/` - ROS 2 Python package for arm simulation, target publishing, UI frontend, and YOLO-based image processing

## ROS 2 workspace

The `ros2_ws/` folder is the main ROS 2 workspace.

### Build

From the workspace root:

```bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### Install dependencies

For ROS 2 Python dependencies:

```bash
cd ros2_ws
rosdep install --from-paths src --ignore-src -y
```

If you get an externally managed environment error on Linux:

```bash
PIP_BREAK_SYSTEM_PACKAGES=1 rosdep install --from-paths src --ignore-src -y
```

## arm_simulation package

The ROS 2 Python package is located at `ros2_ws/arm_simulation`.

It includes these console scripts:

- `target_pub` - publishes target data
- `simulation` - runs the arm simulation logic
- `ui_frontend` - starts the web frontend API layer
- `image_processing` - performs YOLO inference on live camera frames

Refer to `ros2_ws/arm_simulation/arm_simulation/reference/readme.md` for more package-specific details and image-processing notes.

## Notes

- The `arm_simulation` package depends on `fastapi`, `uvicorn[standard]`, `opencv-python`, and `ultralytics`.
- The YOLO model file `yolo26n.pt` is stored in `ros2_ws/arm_simulation/arm_simulation/model/`.
- The `PreRun` folder contains preprocessing and reporting scripts that support the main ROS 2 workspace.

## Contact

Maintainer: `mohnc`
