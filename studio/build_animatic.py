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
        "FRAME_CONFIGS": {}
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
assets_html = ""
if os.path.exists('scene_assets.json'):
    try:
        with open('scene_assets.json', 'r') as f:
            assets = json.load(f)
        for a in assets:
            assets_html += f'<img src="{a["src"]}?v={{Math.random()}}" class="placed-asset" data-src="{a["src"]}" data-id="{a["id"]}" data-x="{a["x"]}" data-y="{a["y"]}" data-scale="{a["scale"]}" style="position: absolute; left: {a["x"]}px; top: {a["y"]}px; transform: translate(-50%, -50%) scale({a["scale"]}); z-index: 10; cursor: move; border: 1px solid transparent; padding: 2px;">\n'
    except Exception as e:
        print("Error loading assets:", e)

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

        <hr style="border-color: #444; margin: 20px 0;">
        
        <h3 style="color: #008CBA;">🧠 ChatGPT Memory</h3>
        <p style="font-size: 12px; color: #aaa; margin-bottom: 5px;">Paste your exact character prompt here so you never lose it!</p>
        <textarea id="prompt-memory" style="width: 100%; height: 80px; background: #222; color: #fff; border: 1px solid #555; border-radius: 4px; padding: 5px; font-size: 12px; box-sizing: border-box;" placeholder="e.g., Anime boy with black hair..."></textarea>
        <button id="save-prompt-btn" style="width: 100%; background: #555; font-size: 14px; margin-top: 5px;" onclick="savePrompt()">💾 Save Master Prompt</button>
    </div>
    
    <div class="scene">
        <img class="bg" src="{background_img}">
        <div id="frames-container"></div>
        {assets_html}
        <div id="ai-prompt-box" style="display: none; position: absolute; z-index: 1000; background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
            <input type="text" id="ai-prompt-input" style="background: rgba(0,0,0,0.5); color: white; border: 1px solid #555; border-radius: 4px; padding: 8px; width: 200px; outline: none;" placeholder="Generate here...">
            <button onclick="submitAiPrompt()" style="padding: 8px 12px; margin-left: 5px; background: #008CBA; border-radius: 4px; border: none; color: white; cursor: pointer; font-weight: bold;">Gen</button>
        </div>
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
            if (activeAsset) {{
                const newX = e.clientX - assetStartX;
                const newY = e.clientY - assetStartY;
                activeAsset.dataset.x = newX;
                activeAsset.dataset.y = newY;
                activeAsset.style.left = newX + 'px';
                activeAsset.style.top = newY + 'px';
                return;
            }}
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

        window.addEventListener('mouseup', () => {{
            isDragging = false;
            activeAsset = null;
        }});

        let activeAsset = null;
        let assetStartX = 0;
        let assetStartY = 0;

        document.querySelectorAll('.placed-asset').forEach(asset => {{
            asset.addEventListener('mousedown', (e) => {{
                if (e.button === 2) return;
                e.stopPropagation(); // Prevent global drag
                activeAsset = asset;
                asset.style.border = "1px dashed #008CBA";
                assetStartX = e.clientX - parseFloat(asset.dataset.x);
                assetStartY = e.clientY - parseFloat(asset.dataset.y);
            }});
            
            asset.addEventListener('wheel', (e) => {{
                e.preventDefault();
                let scale = parseFloat(asset.dataset.scale);
                scale += e.deltaY * -0.001;
                scale = Math.max(0.05, Math.min(scale, 5)); // Limit zoom
                asset.dataset.scale = scale;
                asset.style.transform = `translate(-50%, -50%) scale(${{scale}})`;
            }});
            
            window.addEventListener('mouseup', (e) => {{
                asset.style.border = "1px solid transparent";
            }});
        }});

        let rightClickX = 0;
        let rightClickY = 0;
        
        container.addEventListener('contextmenu', (e) => {{
            e.preventDefault();
            const box = document.getElementById('ai-prompt-box');
            box.style.display = 'block';
            
            const rect = document.querySelector('.scene').getBoundingClientRect();
            // Store coordinates relative to the scene
            rightClickX = e.clientX - rect.left;
            rightClickY = e.clientY - rect.top;
            
            box.style.left = rightClickX + 'px';
            box.style.top = rightClickY + 'px';
            document.getElementById('ai-prompt-input').focus();
        }});
        
        window.addEventListener('click', (e) => {{
            if (e.button !== 2 && !e.target.closest('#ai-prompt-box')) {{
                document.getElementById('ai-prompt-box').style.display = 'none';
            }}
        }});
        
        function submitAiPrompt() {{
            const prompt = document.getElementById('ai-prompt-input').value;
            if (!prompt) return;
            
            const btn = document.querySelector('#ai-prompt-box button');
            btn.innerHTML = 'Generating... ⏳';
            btn.disabled = true;
            document.getElementById('ai-prompt-input').style.display = 'none';
            
            fetch('/generate_asset', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{ prompt: prompt, x: rightClickX, y: rightClickY }})
            }}).then(r => r.json()).then(d => {{
                console.log("Request sent!", d);
                pollStatus();
            }});
        }}

        function pollStatus() {{
            const interval = setInterval(() => {{
                fetch('/check_status').then(r => r.json()).then(d => {{
                    if (d.status === 'done') {{
                        clearInterval(interval);
                        window.location.reload();
                    }}
                }});
            }}, 2000);
        }}

        function saveToServer() {{
            const newComX = BASE_COM_X + globalDx;
            const newComY = BASE_COM_Y + globalDy;
            
            let assetsArray = [];
            document.querySelectorAll('.placed-asset').forEach(a => {{
                assetsArray.push({{
                    id: a.dataset.id,
                    src: a.dataset.src,
                    x: parseFloat(a.dataset.x),
                    y: parseFloat(a.dataset.y),
                    scale: parseFloat(a.dataset.scale)
                }});
            }});

            let payload = {{
                "DEFAULT_COM_X": newComX,
                "DEFAULT_COM_Y": newComY,
                "FRAME_CONFIGS": {{}},
                "ASSETS": assetsArray
            }};
            
            for (let fName in frameOffsets) {{
                if (frameOffsets[fName].x !== 0 || frameOffsets[fName].y !== 0) {{
                    payload.FRAME_CONFIGS[fName] = {{
                        "com_x": newComX + frameOffsets[fName].x,
                        "com_y": newComY + frameOffsets[fName].y
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

        function savePrompt() {{
            const memory = document.getElementById('prompt-memory').value;
            document.getElementById('save-prompt-btn').innerText = "Saving...";
            
            fetch('/save_prompt', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ prompt: memory }})
            }}).then(res => res.json()).then(data => {{
                document.getElementById('save-prompt-btn').innerText = "✅ Saved!";
                setTimeout(() => document.getElementById('save-prompt-btn').innerText = "💾 Save Master Prompt", 2000);
            }}).catch(err => {{
                alert("Error saving: " + err);
                document.getElementById('save-prompt-btn').innerText = "💾 Save Master Prompt";
            }});
        }}
        
        fetch('/get_prompt').then(res => res.json()).then(data => {{
            if (data.prompt) {{
                document.getElementById('prompt-memory').value = data.prompt;
            }}
        }}).catch(e => console.log("No saved prompt yet."));

        // Start playing
        interval = setInterval(playLoop, 1000 / document.getElementById('fps').value);
    </script>
</body>
</html>
"""

with open('preview.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\\nSUCCESS! 18 frames perfectly aligned using Area-Scaling! Visual Editor is ready.")
