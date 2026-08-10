import os
import glob
import re
import numpy as np
from PIL import Image
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, model_complexity=2, min_detection_confidence=0.5)

input_dir = '/home/adnan/Desktop/seji_web/interactive-portfolio/studio/raw_frames'

def extract_number(f):
    s = re.search(r'frame(\d+)', os.path.basename(f))
    return int(s.group(1)) if s else 0

files = sorted(glob.glob(os.path.join(input_dir, '*.png')), key=extract_number)

print("Frame | Torso Len | Hips (X, Y) | Heels (X, Y) | Pose")
print("-" * 70)

for file in files:
    filename = os.path.basename(file)
    frame_num = extract_number(file)
    if frame_num < 3: continue
    
    img = Image.open(file).convert('RGB')
    img_rgb = np.array(img)
    
    results = pose.process(img_rgb)
    
    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        h, w = img.height, img.width
        
        l_sh = (lm[mp_pose.PoseLandmark.LEFT_SHOULDER].x * w, lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y * h)
        r_sh = (lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w, lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h)
        l_hip = (lm[mp_pose.PoseLandmark.LEFT_HIP].x * w, lm[mp_pose.PoseLandmark.LEFT_HIP].y * h)
        r_hip = (lm[mp_pose.PoseLandmark.RIGHT_HIP].x * w, lm[mp_pose.PoseLandmark.RIGHT_HIP].y * h)
        l_heel = (lm[mp_pose.PoseLandmark.LEFT_HEEL].x * w, lm[mp_pose.PoseLandmark.LEFT_HEEL].y * h)
        r_heel = (lm[mp_pose.PoseLandmark.RIGHT_HEEL].x * w, lm[mp_pose.PoseLandmark.RIGHT_HEEL].y * h)
        
        mid_sh = ((l_sh[0] + r_sh[0])/2, (l_sh[1] + r_sh[1])/2)
        mid_hip = ((l_hip[0] + r_hip[0])/2, (l_hip[1] + r_hip[1])/2)
        mid_heel = ((l_heel[0] + r_heel[0])/2, (l_heel[1] + r_heel[1])/2)
        
        torso = np.sqrt((mid_sh[0] - mid_hip[0])**2 + (mid_sh[1] - mid_hip[1])**2)
        
        if mid_heel[1] > mid_hip[1] + 150:
            pose_type = "STANDING"
        else:
            pose_type = "SITTING"
            
        print(f"{filename:8} | {torso:9.2f} | ({mid_hip[0]:4.0f}, {mid_hip[1]:4.0f}) | ({mid_heel[0]:4.0f}, {mid_heel[1]:4.0f}) | {pose_type}")
    else:
        print(f"{filename:8} | NO POSE DETECTED")
