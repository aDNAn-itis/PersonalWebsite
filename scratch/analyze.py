import os
import re
from PIL import Image

raw_frames_dir = '/home/adnan/Desktop/seji_web/interactive-portfolio/studio/raw_frames'

def get_frame_num(filename):
    match = re.search(r'frame(\d+)\.png', filename)
    if match:
        return int(match.group(1))
    return -1

files = [f for f in os.listdir(raw_frames_dir) if f.endswith('.png')]
files.sort(key=get_frame_num)

print("Frame | Image Size | Bbox Size | Bbox Area | Bbox (L, U, R, D)")
print("-" * 70)
for f in files:
    path = os.path.join(raw_frames_dir, f)
    img = Image.open(path)
    img_size = img.size
    
    # If it's RGBA, get the bounding box of non-transparent pixels
    bbox = None
    if img.mode == 'RGBA' or img.mode == 'P':
        # convert to RGBA just to be safe
        img_rgba = img.convert("RGBA")
        bbox = img_rgba.getbbox()
    
    if bbox:
        bw = bbox[2] - bbox[0]
        bh = bbox[3] - bbox[1]
        area = bw * bh
        print(f"{f:7} | {img_size[0]}x{img_size[1]:4} | {bw}x{bh:<4} | {area:9} | {bbox}")
    else:
        print(f"{f:7} | {img_size[0]}x{img_size[1]:4} | No Bbox")

