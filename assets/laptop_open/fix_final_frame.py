import cv2
import numpy as np
import sys
from PIL import Image

# 1. Remove white background from the new bright frame
img = Image.open(sys.argv[1]).convert("RGBA")
data = img.getdata()
new_data = []
for item in data:
    if item[0] > 230 and item[1] > 230 and item[2] > 230:
        new_data.append((255, 255, 255, 0))
    else:
        new_data.append(item)
img.putdata(new_data)
# Resize down to half
img = img.resize((img.width // 2, img.height // 2))
img.save('temp_bright.png')

# 2. Resize and pad to perfectly match f3.png (458x384)
img3 = cv2.imread('f3.png', cv2.IMREAD_UNCHANGED)
img4 = cv2.imread('temp_bright.png', cv2.IMREAD_UNCHANGED)

scale = 0.70 # adjusted scale to match better
new_w = int(img4.shape[1] * scale)
new_h = int(img4.shape[0] * scale)
img4_resized = cv2.resize(img4, (new_w, new_h))

padded4 = np.zeros((384, 458, 4), dtype=np.uint8)
y_offset = 384 - new_h - 10
x_offset = (458 - new_w) // 2
y_offset = max(0, y_offset)
x_offset = max(0, x_offset)

h_to_copy = min(new_h, 384 - y_offset)
w_to_copy = min(new_w, 458 - x_offset)
padded4[y_offset:y_offset+h_to_copy, x_offset:x_offset+w_to_copy] = img4_resized[0:h_to_copy, 0:w_to_copy]

cv2.imwrite('f6.png', padded4)

# 3. Create smoother blending using 3 intermediate frames (we'll overwrite f4, f5 and create f5b if needed, but let's stick to 2 intermediate frames to not change HTML length)
for i in range(1, 3):
    alpha = i / 3.0
    blend = cv2.addWeighted(img3, 1 - alpha, padded4, alpha, 0)
    cv2.imwrite(f'f{3+i}.png', blend)

