import os
import glob
import subprocess
import shutil

INPUT_DIR = 'inputs'
RAW_DIR = 'raw_frames'

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

input_files = glob.glob(os.path.join(INPUT_DIR, '*.png')) + glob.glob(os.path.join(INPUT_DIR, '*.jpg'))

if not input_files:
    print(f"No images found in '{INPUT_DIR}'. Please drop your ChatGPT images there!")
    print(f"Make sure you rename them to frame18.png, frame19.png, etc. so they are sorted correctly.")
    exit(1)

print(f"Found {len(input_files)} images in '{INPUT_DIR}'. Starting High-Quality AI Background Removal...")

for file in input_files:
    filename = os.path.basename(file)
    # Ensure it's saved as PNG in raw_frames
    out_filename = os.path.splitext(filename)[0] + '.png'
    out_path = os.path.join(RAW_DIR, out_filename)
    
    # Run high quality rembg neural network
    print(f"Extracting {filename}...")
    subprocess.run(['rembg', 'i', file, out_path])

print("Background removal complete! Handing over to the Smart Area-Scaling Aligner...")

# Rebuild the animatic
subprocess.run(['python3', 'build_animatic.py'])

print("\\nPIPELINE COMPLETE! Open http://localhost:8000/preview.html to see the results.")
