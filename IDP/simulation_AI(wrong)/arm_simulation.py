import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# ----- Robot parameters -----
L1 = 150.0  # Shoulder → Elbow (mm)
L2 = 120.0  # Elbow → Wrist (mm)

# ----- Joint angles -----
q1 = 0.0  # Base yaw
q2 = 0.0  # Shoulder pitch
q3 = 0.0  # Elbow pitch

# ----- Forward kinematics -----
# Planar coordinates
xp = L1*np.cos(q2) + L2*np.cos(q2 + q3)
zp = L1*np.sin(q2) + L2*np.sin(q2 + q3)

# Convert to 3D (account for yaw rotation q1)
x = xp*np.cos(q1)
y = xp*np.sin(q1)
z = zp

# ----- Joint positions -----
base = np.array([0, 0, 0])
elbow = np.array([
    L1*np.cos(q2)*np.cos(q1),
    L1*np.cos(q2)*np.sin(q1),
    L1*np.sin(q2)
])
wrist = np.array([x, y, z])

# ----- Print results -----
print(f"q (deg) = [{np.degrees(q1):.1f}, {np.degrees(q2):.1f}, {np.degrees(q3):.1f}]")
print(f"EE (mm) = [{x:.1f}, {y:.1f}, {z:.1f}]")

# ----- Draw the arm -----
fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(111, projection='3d')

# Plot arm links
points = np.vstack([base, elbow, wrist])
ax.plot(points[:,0], points[:,1], points[:,2], '-o', color='blue', linewidth=3, markersize=8)

# Coordinate axes labels
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')
ax.set_title('3-DOF Serial Arm (q1=q2=q3=0)')

# Plot limits
reach = L1 + L2
ax.set_xlim(-reach, reach)
ax.set_ylim(-reach, reach)
ax.set_zlim(-0.1*reach, reach)

# Show
plt.show()