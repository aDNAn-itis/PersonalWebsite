import os
import glob
import re
import numpy as np
from PIL import Image

# --- STUDIO CONFIGURATION ---
TARGET_W, TARGET_H = 1774, 887

# Dynamic Alignment Settings
DEFAULT_ANCHOR_X = 437
DEFAULT_ANCHOR_Y = 660
DEFAULT_TARGET_HEIGHT = 480  # Slightly smaller to match frame 12 proportions 

FRAME_CONFIGS = {
    # --- NON-DYNAMIC: Tumbling sequence (falling into bed) ---
    # We disable dynamic cropping here so it uses your EXACT original manual offsets!
    "frame0.png": {"dynamic": False, "offset_x": -420, "offset_y": 10, "rotation": -50, "scale": 0.5},
    "frame1.png": {"dynamic": False, "offset_x": -420, "offset_y": 10, "rotation": -50, "scale": 0.5},
    "frame2.png": {"dynamic": False, "offset_x": -450, "offset_y": -40, "rotation": -10, "scale": 0.5},
    
    # --- DYNAMIC: Sitting frames ---
    # Frame 13 was generated too big by ChatGPT, we scale it down custom here:
    "frame13.png": {"dynamic": True, "target_height": 450},
    
    # --- DYNAMIC: Stand-up sequence ---
    # Since he is standing, his bounding box includes his legs!
    # If we scaled him to 480px, he'd be a tiny dwarf. We increase target_height to 700px
    # so his torso size matches the sitting frames.
    'frame14.png': {'dynamic': True, 'shift_x': 270, 'shift_y': 50, 'target_height': 700},
    'frame15.png': {'dynamic': True, 'shift_x': 270, 'shift_y': 50, 'target_height': 700},
    'frame16.png': {'dynamic': True, 'shift_x': 270, 'shift_y': 50, 'target_height': 700},
    'frame17.png': {'dynamic': True, 'shift_x': 270, 'shift_y': 50, 'target_height': 700}, 
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
    print(f"Found {len(files)} raw frames. Building Animatic with HYBRID PIPELINE...")

def get_content_bbox(img_rgba):
    """Finds the bounding box of the non-transparent character."""
    data = np.array(img_rgba)
    alpha = data[:, :, 3]
    rgb = data[:, :, :3]
    
    is_not_transparent = alpha > 10
    is_not_white = (rgb[:, :, 0] < 240) | (rgb[:, :, 1] < 240) | (rgb[:, :, 2] < 240)
    mask = is_not_transparent & is_not_white
    
    y_coords, x_coords = np.where(mask)
    if len(x_coords) > 0:
        return (np.min(x_coords), np.min(y_coords), np.max(x_coords), np.max(y_coords))
    return None

for file in files:
    filename = os.path.basename(file)
    
    # Load configs
    config = FRAME_CONFIGS.get(filename, {})
    is_dynamic = config.get("dynamic", True) # Default to dynamic
    
    img = Image.open(file).convert('RGBA')
    canvas = Image.new('RGBA', (TARGET_W, TARGET_H), (0, 0, 0, 0))
    
    if not is_dynamic:
        # --- OLD LEGACY MODE (For Tumbling Frames) ---
        frame_scale = config.get("scale", 0.5)
        frame_rot = config.get("rotation", 0)
        frame_ox = config.get("offset_x", -450)
        frame_oy = config.get("offset_y", -40)
        
        new_w = int(img.width * frame_scale)
        new_h = int(img.height * frame_scale)
        resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        if frame_rot != 0:
            resized_img = resized_img.rotate(frame_rot, expand=True, resample=Image.Resampling.BICUBIC)
            new_w, new_h = resized_img.size
            
        paste_x = (TARGET_W - new_w) // 2 + frame_ox
        paste_y = (TARGET_H - new_h) // 2 + frame_oy
        canvas.paste(resized_img, (paste_x, paste_y), resized_img)
        canvas.save(os.path.join(output_dir, filename))
        print(f"Processed {filename}: [LEGACY] Placed with offset ({frame_ox}, {frame_oy})")
        
    else:
        # --- NEW DYNAMIC MODE (For Sitting and Standing Frames) ---
        shift_x = config.get("shift_x", 0)
        shift_y = config.get("shift_y", 0)
        frame_rot = config.get("rotation", 0)
        target_height = config.get("target_height", DEFAULT_TARGET_HEIGHT)
        
        anchor_x = DEFAULT_ANCHOR_X + shift_x
        anchor_y = DEFAULT_ANCHOR_Y + shift_y
        
        bbox = get_content_bbox(img)
        if bbox:
            left, top, right, bottom = bbox
            img = img.crop((left, top, right, bottom))
        
        current_height = img.height
        scale_factor = target_height / current_height if current_height > 0 else 1.0
        new_w = int(img.width * scale_factor)
        new_h = int(img.height * scale_factor)
        
        resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        if frame_rot != 0:
            resized_img = resized_img.rotate(frame_rot, expand=True, resample=Image.Resampling.BICUBIC)
            new_w, new_h = resized_img.size
            
        paste_x = int(anchor_x - (new_w / 2))
        paste_y = int(anchor_y - new_h)
        
        canvas.paste(resized_img, (paste_x, paste_y), resized_img)
        canvas.save(os.path.join(output_dir, filename))
        print(f"Processed {filename}: [DYNAMIC] Normalized height to {target_height}px, Pinned to ({anchor_x}, {anchor_y})")

# Generate Web Previewer
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

print(f"\\nSUCCESS! {len(files)} frames aligned with HYBRID PIPELINE.")
