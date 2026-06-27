```
cd /home/mohnc/ros2_ws
rosdep install --from-paths src --ignore-src -y
rosdep update
```

```
PIP_BREAK_SYSTEM_PACKAGES=1 rosdep install --from-paths src --ignore-src -y
```

**Note:** If you encounter a PEP 668 error about pip installing alongside externally managed packages, use the `PIP_BREAK_SYSTEM_PACKAGES=1` environment variable. This is required in Python 3.11+ to allow pip to install packages globally.