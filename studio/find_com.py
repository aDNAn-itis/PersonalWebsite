import os
import numpy as np
from PIL import Image

frames = ['frame2.png', 'frame3.png', 'frame4.png']
input_dir = 'raw_frames'

print("Analyzing Character Center of Mass (ignoring white/transparent backgrounds)...")

base_cx, base_cy = None, None

for f in frames:
    path = os.path.join(input_dir, f)
    if os.path.exists(path):
        img = Image.open(path).convert("RGBA")
        data = np.array(img)
        
        # Create a mask for "actual character pixels"
        # Not transparent (alpha > 10) AND Not white (R<240 or G<240 or B<240)
        alpha = data[:, :, 3]
        rgb = data[:, :, :3]
        
        is_not_transparent = alpha > 10
        is_not_white = (rgb[:, :, 0] < 240) | (rgb[:, :, 1] < 240) | (rgb[:, :, 2] < 240)
        
        mask = is_not_transparent & is_not_white
        
        # Get coordinates of all valid pixels
        y_coords, x_coords = np.where(mask)
        
        if len(x_coords) > 0:
            cx = int(np.mean(x_coords))
            cy = int(np.mean(y_coords))
            print(f"{f}: Character CoM = ({cx}, {cy})")
            
            if f == 'frame2.png':
                base_cx, base_cy = cx, cy
                print(f"  -> Using as baseline. Offset: 0, 0")
            else:
                diff_x = base_cx - cx
                diff_y = base_cy - cy
                # To align them perfectly with frame2's CoM, we must shift them by diff_x, diff_y
                print(f"  -> Difference from frame2: X={diff_x}, Y={diff_y}")
                print(f"  -> Recommended FRAME_CONFIGS: offset_x: {-350 + diff_x}, offset_y: {-40 + diff_y}")
        else:
            print(f"{f}: No valid pixels found")
