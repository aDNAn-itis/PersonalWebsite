import os
from rembg import remove
from PIL import Image

frames = ['frame2.png', 'frame3.png']
input_dir = 'raw_frames'

for f in frames:
    path = os.path.join(input_dir, f)
    if os.path.exists(path):
        print(f"Processing {path}...")
        input_image = Image.open(path)
        output_image = remove(input_image)
        output_image.save(path)
        print(f"Saved {path} with transparent background.")
