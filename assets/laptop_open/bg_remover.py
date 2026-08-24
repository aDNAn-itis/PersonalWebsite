import sys
from PIL import Image

img = Image.open(sys.argv[1]).convert("RGBA")
data = img.getdata()
new_data = []

# Simple magic wand for white background
for item in data:
    if item[0] > 230 and item[1] > 230 and item[2] > 230:
        new_data.append((255, 255, 255, 0))
    else:
        new_data.append(item)

img.putdata(new_data)
# Also resize it a bit so it fits the scene nicely
img = img.resize((img.width // 2, img.height // 2))
img.save(sys.argv[2])
