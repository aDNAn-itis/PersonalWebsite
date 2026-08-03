from PIL import Image
import os

frames = ['frame2.png', 'frame3.png', 'frame4.png', 'frame5.png']
input_dir = 'raw_frames'

print("Analyzing Center of Gravity for frames...")

for f in frames:
    path = os.path.join(input_dir, f)
    if os.path.exists(path):
        img = Image.open(path).convert("RGBA")
        bbox = img.getbbox() # Returns (left, upper, right, lower)
        if bbox:
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            print(f"{f}:")
            print(f"  Bounding Box: {bbox}")
            print(f"  Center: ({center_x}, {center_y})")
            print(f"  Size: {width}x{height}")
        else:
            print(f"{f}: Empty image")
