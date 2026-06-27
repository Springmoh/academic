import cv2
import os

# Folder to save frames
frame_folder = "saved_frames"
os.makedirs(frame_folder, exist_ok=True)

# Open camera on Ubuntu
cap = cv2.VideoCapture("/dev/video4")
# You can also try:
# cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera. Try /dev/video1 or check camera permission.")
    exit()

# Camera properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 30

# Save video
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter("recorded_video.mp4", fourcc, fps, (frame_width, frame_height))

frame_count = 0

print("Recording... Press q to stop.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Write frame into video
    out.write(frame)

    # Save each frame as image
    frame_path = os.path.join(frame_folder, f"frame_{frame_count:05d}.jpg")
    cv2.imwrite(frame_path, frame)

    cv2.imshow("Ubuntu Camera Recording", frame)

    frame_count += 1

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print("Saved video: recorded_video.mp4")
print(f"Saved frames folder: {frame_folder}")