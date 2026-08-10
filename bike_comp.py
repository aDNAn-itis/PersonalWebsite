from PIL import Image
import os

frames = [f'assets/scene2/frame{i}.png' for i in range(1, 9)]
images = [Image.open(f).convert("RGBA") for f in frames if os.path.exists(f)]

if images:
    w, h = images[0].size
    grid_w = w * len(images)
    grid_h = h
    out_img = Image.new('RGBA', (grid_w, grid_h))
    
    for i, img in enumerate(images):
        out_img.paste(img, (i * w, 0))
    
    out_img.save('scratch/bike_comp.png')
    print("Saved scratch/bike_comp.png")
