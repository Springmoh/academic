import cv2
import os

video_path = "/home/mohnc/Desktop/File/academic/IDP/test/output2.mp4" # your video file
output_folder = "/home/mohnc/Desktop/File/academic/IDP/output2"       # folder to save frames

os.makedirs(output_folder, exist_ok=True)

cap = cv2.VideoCapture(video_path)

frame_count = 1469

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_name = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
    cv2.imwrite(frame_name, frame)
    frame_count += 1

cap.release()
print(f"Done. Extracted {frame_count} frames.")
