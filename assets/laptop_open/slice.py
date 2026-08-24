import sys
from PIL import Image

def slice_and_remove_bg():
    img_path = sys.argv[1]
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    
    # Grid is 3 columns, 2 rows
    cols = 3
    rows = 2
    cell_w = w // cols
    cell_h = h // rows
    
    frame_idx = 0
    for r in range(rows):
        for c in range(cols):
            box = (c * cell_w, r * cell_h, (c + 1) * cell_w, (r + 1) * cell_h)
            cell = img.crop(box)
            
            # Simple white background removal
            data = cell.getdata()
            new_data = []
            for item in data:
                # If pixel is close to white, make it transparent
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            cell.putdata(new_data)
            
            cell.save(f"assets/laptop_open/frame_{frame_idx}.png")
            frame_idx += 1

if __name__ == "__main__":
    slice_and_remove_bg()
