import os
import glob
from PIL import Image

# --- STUDIO CONFIGURATION ---
TARGET_W, TARGET_H = 1774, 887

# This is the scale factor applied to the ENTIRE raw image.
# It ensures every frame is scaled identically, preserving alignment.
# We set this to 1.35 to perfectly match the size the cycle had in your website!
SCALE_FACTOR = 1.35  

input_dir = 'raw_frames'
output_dir = 'aligned_frames'
background_img = '../../assets/scene2/road_background.png'

os.makedirs(output_dir, exist_ok=True)

files = sorted(glob.glob(os.path.join(input_dir, '*.png')))
if not files:
    print(f"No PNG files found in {input_dir}/.")
    exit()

print(f"Found {len(files)} raw frames. Building Animatic without dynamic cropping...")

for file in files:
    filename = os.path.basename(file)
    img = Image.open(file).convert('RGBA')
    
    # 1. Scale the ENTIRE image uniformly. 
    # We DO NOT crop the bounding box, because cropping dynamically changes 
    # the center of mass in every frame and destroys the artist's alignment!
    new_w = int(img.width * SCALE_FACTOR)
    new_h = int(img.height * SCALE_FACTOR)
    
    resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # 2. Paste into Golden Canvas (Dead Center)
    canvas = Image.new('RGBA', (TARGET_W, TARGET_H), (0, 0, 0, 0))
    paste_x = (TARGET_W - new_w) // 2
    
    # Push it down slightly to sit on the road (can adjust this Y offset)
    # Since we scaled it up by 1.35, we adjust the paste_y so the wheels hit the road
    paste_y = (TARGET_H - new_h) // 2 + 100 
    
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
