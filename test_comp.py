from PIL import Image
import os

bg_path = 'assets/scene_bedroom/bedroom_bg_cropped.jpg'
bg = Image.open(bg_path).convert("RGBA")

frames = [17, 18, 19, 20, 21, 22, 23]
offsets = {
    17: (-360, 50),
    18: (-450, 150),
    19: (-450, 150),
    20: (-450, 150),
    21: (-450, 150),
    22: (-450, 150),
    23: (-450, 150)
}

grid_w = bg.width * len(frames)
grid_h = bg.height
out_img = Image.new('RGBA', (grid_w, grid_h))

for i, f in enumerate(frames):
    img = bg.copy()
    fg_path = f'studio/raw_frames/frame{f}.png'
    if os.path.exists(fg_path):
        fg = Image.open(fg_path).convert("RGBA")
        off_x, off_y = offsets[f]
        img.paste(fg, (off_x, off_y), fg)
    out_img.paste(img, (i * bg.width, 0))

out_img.save('scratch/comp_17_23.png')
print("Saved scratch/comp_17_23.png")
