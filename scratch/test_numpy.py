import os
import glob
import re
import numpy as np
from PIL import Image

input_dir = '/home/adnan/Desktop/seji_web/interactive-portfolio/studio/raw_frames'

def extract_number(f):
    s = re.search(r'frame(\d+)', os.path.basename(f))
    return int(s.group(1)) if s else 0

files = sorted(glob.glob(os.path.join(input_dir, '*.png')), key=extract_number)

print("Frame | Pixel Area | CoM (X, Y) | BBox Height")
print("-" * 60)

for file in files:
    filename = os.path.basename(file)
    frame_num = extract_number(file)
    
    img = Image.open(file).convert('RGBA')
    data = np.array(img)
    alpha = data[:, :, 3]
    rgb = data[:, :, :3]
    
    is_not_transparent = alpha > 10
    is_not_white = (rgb[:, :, 0] < 240) | (rgb[:, :, 1] < 240) | (rgb[:, :, 2] < 240)
    mask = is_not_transparent & is_not_white
    
    y_coords, x_coords = np.where(mask)
    if len(x_coords) > 0:
        area = len(x_coords)
        cx = np.mean(x_coords)
        cy = np.mean(y_coords)
        bbox_h = np.max(y_coords) - np.min(y_coords)
        print(f"{filename:8} | {area:10d} | ({cx:6.1f}, {cy:6.1f}) | {bbox_h:4d}")
    else:
        print(f"{filename:8} | EMPTY")
