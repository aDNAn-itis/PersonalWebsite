import os
import glob
import re
from PIL import Image

# --- STUDIO CONFIGURATION ---
TARGET_W, TARGET_H = 1774, 887

# Default fallbacks (used if a frame is not in FRAME_CONFIGS)
OFFSET_X = -450
OFFSET_Y = -40
ROTATION_ANGLE = -10  # Negative numbers rotate clockwise
SCALE_FACTOR = 0.5

# Per-frame precise alignments
FRAME_CONFIGS = {
    "frame0.png": {"offset_x": -420, "offset_y": 10, "rotation": -50, "scale": 0.5},
    "frame1.png": {"offset_x": -420, "offset_y": 10, "rotation": -50, "scale": 0.5},
    "frame2.png": {"offset_x": -450, "offset_y": -40, "rotation": -10, "scale": 0.5}
}

input_dir = 'raw_frames'
output_dir = 'aligned_frames'
background_img = '../assets/scene_bedroom/bedroom_background.png'

os.makedirs(output_dir, exist_ok=True)

def extract_number(f):
    s = re.search(r'\d+', os.path.basename(f))
    return int(s.group()) if s else 0

files = sorted(glob.glob(os.path.join(input_dir, '*.png')), key=extract_number)
if not files:
    print(f"No PNG frames found in {input_dir}/. Generating Empty Room Preview...")
else:
    print(f"Found {len(files)} raw frames. Building Animatic without dynamic cropping...")

for file in files:
    filename = os.path.basename(file)
    
    # Get config for this frame
    config = FRAME_CONFIGS.get(filename, {})
    frame_scale = config.get("scale", SCALE_FACTOR)
    frame_rot = config.get("rotation", ROTATION_ANGLE)
    frame_ox = config.get("offset_x", OFFSET_X)
    frame_oy = config.get("offset_y", OFFSET_Y)
    
    img = Image.open(file).convert('RGBA')
    
    # 1. Resize and Rotate Image
    new_w = int(img.width * frame_scale)
    new_h = int(img.height * frame_scale)
    
    resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Apply rotation
    if frame_rot != 0:
        resized_img = resized_img.rotate(frame_rot, expand=True, resample=Image.Resampling.BICUBIC)
        new_w, new_h = resized_img.size
        
    # 2. Paste into Golden Canvas (Dead Center + Offsets)
    canvas = Image.new('RGBA', (TARGET_W, TARGET_H), (0, 0, 0, 0))
    paste_x = (TARGET_W - new_w) // 2 + frame_ox
    paste_y = (TARGET_H - new_h) // 2 + frame_oy
    
    canvas.paste(resized_img, (paste_x, paste_y), resized_img)
    canvas.save(os.path.join(output_dir, filename))
    print(f"Processed {filename}: Preserved original canvas alignment.")

# Generate the Instant Web Previewer
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Scene Studio Animatic</title>
    <style>
        body {{ background: #111; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
        .scene {{ position: relative; width: 1774px; height: 887px; max-width: 95vw; max-height: 95vh; aspect-ratio: 1774/887; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.8); border: 1px solid #333; }}
        .bg {{ position: absolute; width: 100%; height: 100%; object-fit: cover; }}
        .frame {{ position: absolute; width: 100%; height: 100%; object-fit: cover; opacity: 0; }}
        .active {{ opacity: 1; }}
        
        #controls {{ position: absolute; top: 20px; left: 20px; z-index: 100; background: rgba(0,0,0,0.85); padding: 15px; color: white; font-family: monospace; border-radius: 8px; border: 1px solid #444; }}
        button {{ padding: 5px 15px; cursor: pointer; background: #fff; border: none; font-weight: bold; border-radius: 4px; }}
        input {{ width: 50px; text-align: center; font-weight: bold; }}
    </style>
</head>
<body>
    <div id="controls">
        <h3 style="margin: 0 0 10px 0; color: #4CAF50;">Animatic Previewer</h3>
        <label>Speed (FPS): <input type="number" id="fps" value="6"></label>
        <button onclick="updateFPS()">Update</button>
    </div>
    
    <div class="scene">
        <img class="bg" src="{background_img}">
        <div id="frames-container"></div>
    </div>

    <script>
        const frames = {str([os.path.join(output_dir, os.path.basename(f)) for f in files])};
        const container = document.getElementById('frames-container');
        
        frames.forEach((src, index) => {{
            const img = document.createElement('img');
            img.src = src + '?v=' + Math.random();
            img.className = 'frame' + (index === 0 ? ' active' : '');
            img.id = 'frame-' + index;
            container.appendChild(img);
        }});

        let currentFrame = 0;
        let intervalTime = 1000 / 6;
        let interval;

        function play() {{
            clearInterval(interval);
            interval = setInterval(() => {{
                document.getElementById('frame-' + currentFrame).classList.remove('active');
                currentFrame = (currentFrame + 1) % frames.length;
                document.getElementById('frame-' + currentFrame).classList.add('active');
            }}, intervalTime);
        }}

        function updateFPS() {{
            const fps = document.getElementById('fps').value;
            intervalTime = 1000 / fps;
            play();
        }}

        play();
    </script>
</body>
</html>
"""

with open('preview.html', 'w') as f:
    f.write(html_content)

print(f"\\nSUCCESS! {len(files)} frames aligned.")
