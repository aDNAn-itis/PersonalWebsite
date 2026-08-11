import cv2
import numpy as np
import os

video_path = "../scratch/video_hd.mp4"
monitor_path = "/home/adnan/.gemini/antigravity-cli/brain/46f94dc1-6caa-4bd3-9fc0-b134c51ddf04/straight_monitor_1786433770373.jpg"

print("Loading monitor image...")
monitor = cv2.imread(monitor_path)
h, w = monitor.shape[:2]

# Find the black screen (thresholding for very dark pixels)
gray = cv2.cvtColor(monitor, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY_INV)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Get largest contour (the screen)
largest = max(contours, key=cv2.contourArea)
x, y, sw, sh = cv2.boundingRect(largest)

print(f"Screen bounding box found at: x={x}, y={y}, w={sw}, h={sh}")

print("Extracting 8 frames from video...")
cap = cv2.VideoCapture(video_path)
# Skip to 10 seconds (assume 30fps -> 300 frames)
cap.set(cv2.CAP_PROP_POS_FRAMES, 300)

frames = []
for i in range(40):
    ret, frame = cap.read()
    if not ret: break
    # Resize video frame to fit screen bounding box
    frame_resized = cv2.resize(frame, (sw, sh))
    
    # Composite onto monitor
    monitor_copy = monitor.copy()
    monitor_copy[y:y+sh, x:x+sw] = frame_resized
    frames.append(monitor_copy)

cap.release()

print("Building composite spritesheet...")
spritesheet = np.hstack(frames)

cv2.imwrite("../scratch/test_spritesheet.png", spritesheet)
print("Saved to ../scratch/test_spritesheet.png at FULL resolution!")
