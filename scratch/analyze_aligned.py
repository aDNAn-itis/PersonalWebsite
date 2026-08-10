import os
import glob
import re
import numpy as np
from PIL import Image

output_dir = '/home/adnan/Desktop/seji_web/interactive-portfolio/studio/aligned_frames'

def extract_number(f):
    s = re.search(r'frame(\d+)', os.path.basename(f))
    return int(s.group(1)) if s else 0

files = sorted(glob.glob(os.path.join(output_dir, '*.png')), key=extract_number)

print("Frame | Aligned Image Size | Character BBox | Char Width x Height | Char Center (X, Y)")
print("-" * 90)

def get_content_bbox(img_rgba):
    data = np.array(img_rgba)
    alpha = data[:, :, 3]
    y_coords, x_coords = np.where(alpha > 10)
    if len(x_coords) > 0:
        return (np.min(x_coords), np.min(y_coords), np.max(x_coords), np.max(y_coords))
    return None

for file in files:
    filename = os.path.basename(file)
    img = Image.open(file).convert('RGBA')
    bbox = get_content_bbox(img)
    
    if bbox:
        l, t, r, b = bbox
        w = r - l
        h = b - t
        cx = l + w//2
        cy = t + h//2
        print(f"{filename:8} | {img.size[0]}x{img.size[1]} | ({l:4},{t:4},{r:4},{b:4}) | {w:4} x {h:4} | ({cx:4}, {cy:4})")
    else:
        print(f"{filename:8} | Empty")
