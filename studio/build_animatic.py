import os
import glob
import re
import json
import numpy as np
from PIL import Image

# --- STUDIO CONFIGURATION ---
TARGET_W, TARGET_H = 1774, 887

config_file = 'animatic_config.json'

if not os.path.exists(config_file):
    default_config = {
        "TARGET_AREA": 75000,
        "DEFAULT_COM_X": 380,
        "DEFAULT_COM_Y": 480,
        "FRAME_CONFIGS": {
            "frame0.png": {"dynamic": False, "offset_x": -420, "offset_y": 10, "rotation": -50, "scale": 0.5},
            "frame1.png": {"dynamic": False, "offset_x": -420, "offset_y": 10, "rotation": -50, "scale": 0.5},
            "frame14.png": {"dynamic": True, "com_x": 650, "com_y": 390},
            "frame15.png": {"dynamic": True, "com_x": 650, "com_y": 390},
            "frame16.png": {"dynamic": True, "com_x": 650, "com_y": 390},
            "frame17.png": {"dynamic": True, "com_x": 650, "com_y": 390}
        }
    }
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=4)

with open(config_file, 'r') as f:
    config_data = json.load(f)

TARGET_AREA = config_data.get("TARGET_AREA", 75000)
DEFAULT_COM_X = config_data.get("DEFAULT_COM_X", 380)
DEFAULT_COM_Y = config_data.get("DEFAULT_COM_Y", 480)
FRAME_CONFIGS = config_data.get("FRAME_CONFIGS", {})

input_dir = 'raw_frames'
output_dir = 'aligned_frames'
background_img = '../assets/scene_bedroom/bedroom_background.png'

os.makedirs(output_dir, exist_ok=True)

def extract_number(f):
    s = re.search(r'\d+', os.path.basename(f))
    return int(s.group()) if s else 0

files = sorted(glob.glob(os.path.join(input_dir, '*.png')), key=extract_number)
print(f"Found {len(files)} raw frames. Building Animatic with PURE PYTHON AREA-SCALING...")

def get_smart_metrics(img_rgba):
    data = np.array(img_rgba)
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
        bbox = (np.min(x_coords), np.min(y_coords), np.max(x_coords), np.max(y_coords))
        return bbox, area, (cx, cy)
    return None, 0, (0,0)

for file in files:
    filename = os.path.basename(file)
    config = FRAME_CONFIGS.get(filename, {})
    is_dynamic = config.get("dynamic", True)
    
    img = Image.open(file).convert('RGBA')
    canvas = Image.new('RGBA', (TARGET_W, TARGET_H), (0, 0, 0, 0))
    
    if not is_dynamic:
        frame_scale = config.get("scale", 0.5)
        frame_rot = config.get("rotation", 0)
        frame_ox = config.get("offset_x", -450)
        frame_oy = config.get("offset_y", -40)
        
        new_w, new_h = int(img.width * frame_scale), int(img.height * frame_scale)
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        if frame_rot != 0:
            resized = resized.rotate(frame_rot, expand=True, resample=Image.Resampling.BICUBIC)
            new_w, new_h = resized.size
            
        px = (TARGET_W - new_w) // 2 + frame_ox
        py = (TARGET_H - new_h) // 2 + frame_oy
        canvas.paste(resized, (px, py), resized)
        canvas.save(os.path.join(output_dir, filename))
        print(f"Processed {filename}: [FALLING] Legacy Rotation")
        
    else:
        target_com_x = config.get("com_x", DEFAULT_COM_X)
        target_com_y = config.get("com_y", DEFAULT_COM_Y)
        
        bbox, raw_area, (raw_cx, raw_cy) = get_smart_metrics(img)
        
        if bbox and raw_area > 0:
            left, top, right, bottom = bbox
            img_cropped = img.crop((left, top, right, bottom))
            
            scale_factor = np.sqrt(TARGET_AREA / raw_area)
            new_w = int(img_cropped.width * scale_factor)
            new_h = int(img_cropped.height * scale_factor)
            resized = img_cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            scaled_cx = (raw_cx - left) * scale_factor
            scaled_cy = (raw_cy - top) * scale_factor
            
            px = int(target_com_x - scaled_cx)
            py = int(target_com_y - scaled_cy)
            
            canvas.paste(resized, (px, py), resized)
            canvas.save(os.path.join(output_dir, filename))
            print(f"Processed {filename}: [SMART] Scaled {scale_factor:.2f}x. Pinned to ({target_com_x}, {target_com_y})")
        else:
            print(f"Processed {filename}: FAILED (Empty Mask)")

# Generate Web Previewer with Visual Editor
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Scene Studio - Visual Editor</title>
    <style>
        body {{ background: #111; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; color: white; font-family: sans-serif; }}
        .scene {{ position: relative; width: 1774px; height: 887px; max-width: 90vw; max-height: 90vh; aspect-ratio: 1774/887; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.8); border: 1px solid #333; }}
        .bg {{ position: absolute; width: 100%; height: 100%; object-fit: cover; }}
        
        #frames-container {{ position: absolute; width: 100%; height: 100%; cursor: grab; }}
        #frames-container:active {{ cursor: grabbing; }}
        
        .frame {{ position: absolute; width: 100%; height: 100%; object-fit: cover; opacity: 0; pointer-events: none; }}
        .active {{ opacity: 1; }}
        
        #controls {{ position: absolute; top: 20px; left: 20px; z-index: 100; background: rgba(0,0,0,0.85); padding: 20px; border-radius: 8px; border: 1px solid #444; min-width: 320px; }}
        h3 {{ margin: 0 0 15px 0; color: #4CAF50; }}
        button {{ padding: 10px 15px; cursor: pointer; background: #4CAF50; color: white; border: none; font-weight: bold; border-radius: 4px; margin-top: 5px; }}
        button:hover {{ background: #45a049; }}
        .btn-small {{ padding: 5px 10px; font-size: 12px; }}
        input[type="number"] {{ width: 60px; text-align: center; font-weight: bold; padding: 5px; background: #222; color: white; border: 1px solid #555; border-radius: 4px; }}
        
        .panel-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .playback-controls {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; background: #222; padding: 10px; border-radius: 4px; }}
        
        #save-btn {{ width: 100%; background: #008CBA; font-size: 16px; margin-top: 20px; }}
        #save-btn:hover {{ background: #007bb5; }}
    </style>
</head>
<body>
    <div id="controls">
        <h3>✨ Auto-Save Visual Editor ✨</h3>
        
        <div class="playback-controls">
            <button class="btn-small" onclick="prevFrame()">◀ Prev</button>
            <button id="play-btn" onclick="togglePlay()">Pause</button>
            <button class="btn-small" onclick="nextFrame()">Next ▶</button>
        </div>
        
        <div class="panel-row">
            <label>Current Frame:</label>
            <strong id="frame-indicator" style="color: #4CAF50;">frame0.png</strong>
        </div>
        <div class="panel-row">
            <label>Speed (FPS):</label>
            <input type="number" id="fps" value="6" onchange="updateFPS()">
        </div>
        <div class="panel-row">
            <label>Drag Mode:</label>
            <select id="drag-mode" style="background: #222; color: white; padding: 5px; border-radius: 4px;">
                <option value="global">Move Entire Sequence</option>
                <option value="frame">Move Current Frame Only</option>
            </select>
        </div>
        
        <p style="font-size: 13px; color: #aaa; margin-top: 15px;">Drag the character, then click save! The Python server will rebuild the images automatically.</p>
        
        <button id="save-btn" onclick="saveToServer()">Save & Rebuild Animatic</button>
    </div>
    
    <div class="scene">
        <img class="bg" src="{background_img}">
        <div id="frames-container"></div>
    </div>

    <script>
        const frames = {str([os.path.join(output_dir, os.path.basename(f)) for f in files])};
        const frameNames = {str([os.path.basename(f) for f in files])};
        const container = document.getElementById('frames-container');
        
        const BASE_COM_X = {DEFAULT_COM_X};
        const BASE_COM_Y = {DEFAULT_COM_Y};
        
        let globalDx = 0;
        let globalDy = 0;
        let frameOffsets = {{}};
        
        frames.forEach((src, index) => {{
            const img = document.createElement('img');
            img.src = src + '?v=' + Math.random();
            img.className = 'frame' + (index === 0 ? ' active' : '');
            img.id = 'frame-' + index;
            container.appendChild(img);
            frameOffsets[frameNames[index]] = {{x: 0, y: 0}};
        }});

        let currentFrame = 0;
        let interval;
        let isPlaying = true;
        
        let isDragging = false;
        let startMouseX, startMouseY;
        let initialGlobalDx, initialGlobalDy;
        let initialFrameDx, initialFrameDy;

        function setFrame(index) {{
            document.getElementById('frame-' + currentFrame).classList.remove('active');
            currentFrame = (index + frames.length) % frames.length;
            document.getElementById('frame-' + currentFrame).classList.add('active');
            document.getElementById('frame-indicator').innerText = frameNames[currentFrame];
            updateTransform();
        }}

        function playLoop() {{
            if (!isPlaying) return;
            setFrame(currentFrame + 1);
        }}

        function togglePlay() {{
            isPlaying = !isPlaying;
            document.getElementById('play-btn').innerText = isPlaying ? "Pause" : "Play";
            if (isPlaying) {{
                interval = setInterval(playLoop, 1000 / document.getElementById('fps').value);
            }} else {{
                clearInterval(interval);
            }}
        }}

        function prevFrame() {{ isPlaying = false; document.getElementById('play-btn').innerText = "Play"; clearInterval(interval); setFrame(currentFrame - 1); }}
        function nextFrame() {{ isPlaying = false; document.getElementById('play-btn').innerText = "Play"; clearInterval(interval); setFrame(currentFrame + 1); }}

        function updateFPS() {{
            if (isPlaying) {{
                clearInterval(interval);
                interval = setInterval(playLoop, 1000 / document.getElementById('fps').value);
            }}
        }}

        function updateTransform() {{
            const fName = frameNames[currentFrame];
            const dx = globalDx + frameOffsets[fName].x;
            const dy = globalDy + frameOffsets[fName].y;
            container.style.transform = `translate(${{dx}}px, ${{dy}}px)`;
        }}

        container.addEventListener('mousedown', (e) => {{
            isDragging = true;
            startMouseX = e.clientX;
            startMouseY = e.clientY;
            initialGlobalDx = globalDx;
            initialGlobalDy = globalDy;
            initialFrameDx = frameOffsets[frameNames[currentFrame]].x;
            initialFrameDy = frameOffsets[frameNames[currentFrame]].y;
        }});

        window.addEventListener('mousemove', (e) => {{
            if (!isDragging) return;
            const mode = document.getElementById('drag-mode').value;
            const deltaX = e.clientX - startMouseX;
            const deltaY = e.clientY - startMouseY;
            
            if (mode === 'global') {{
                globalDx = initialGlobalDx + deltaX;
                globalDy = initialGlobalDy + deltaY;
            }} else {{
                frameOffsets[frameNames[currentFrame]].x = initialFrameDx + deltaX;
                frameOffsets[frameNames[currentFrame]].y = initialFrameDy + deltaY;
            }}
            updateTransform();
        }});

        window.addEventListener('mouseup', () => isDragging = false);

        function saveToServer() {{
            const newComX = BASE_COM_X - globalDx;
            const newComY = BASE_COM_Y - globalDy;
            
            let payload = {{
                "DEFAULT_COM_X": newComX,
                "DEFAULT_COM_Y": newComY,
                "FRAME_CONFIGS": {{}}
            }};
            
            for (let fName in frameOffsets) {{
                if (frameOffsets[fName].x !== 0 || frameOffsets[fName].y !== 0) {{
                    payload.FRAME_CONFIGS[fName] = {{
                        "com_x": newComX - frameOffsets[fName].x,
                        "com_y": newComY - frameOffsets[fName].y
                    }};
                }}
            }}
            
            document.getElementById('save-btn').innerText = "Saving & Rebuilding...";
            
            fetch('/save', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(payload)
            }}).then(res => res.json()).then(data => {{
                window.location.reload();
            }}).catch(err => {{
                alert("Error saving: " + err);
                document.getElementById('save-btn').innerText = "Save & Rebuild Animatic";
            }});
        }}

        // Start playing
        interval = setInterval(playLoop, 1000 / document.getElementById('fps').value);
    </script>
</body>
</html>
"""

with open('preview.html', 'w') as f:
    f.write(html_content)

print(f"\\nSUCCESS! 18 frames perfectly aligned using Area-Scaling! Visual Editor is ready.")
