import os
import numpy as np
from PIL import Image

frames = [f'frame{i}.png' for i in range(12, 18)]
input_dir = 'raw_frames'

for f in frames:
    path = os.path.join(input_dir, f)
    if os.path.exists(path):
        img = Image.open(path).convert("RGBA")
        data = np.array(img)
        alpha = data[:, :, 3]
        rgb = data[:, :, :3]
        
        is_not_transparent = alpha > 10
        is_not_white = (rgb[:, :, 0] < 240) | (rgb[:, :, 1] < 240) | (rgb[:, :, 2] < 240)
        mask = is_not_transparent & is_not_white
        y_coords, x_coords = np.where(mask)
        
        if len(x_coords) > 0:
            cx = int(np.mean(x_coords))
            cy = int(np.mean(y_coords))
            bottom_y = np.max(y_coords)
            left_x = np.min(x_coords)
            right_x = np.max(x_coords)
            print(f"{f}: CoM=({cx}, {cy}), bottom_y={bottom_y}, left_x={left_x}, right_x={right_x}")
