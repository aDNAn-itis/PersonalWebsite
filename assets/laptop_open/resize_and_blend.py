import cv2
import numpy as np

# Load frames
img3 = cv2.imread('frame_3.png', cv2.IMREAD_UNCHANGED)
img4 = cv2.imread('frame_4.png', cv2.IMREAD_UNCHANGED)

# Resize img4 to roughly match the size/width of img3
# img3 is 458x384. 
# We'll scale img4 down by a factor to make it match visually.
scale = 0.75
new_w = int(img4.shape[1] * scale)
new_h = int(img4.shape[0] * scale)
img4_resized = cv2.resize(img4, (new_w, new_h))

# Pad img4_resized to match img3 exact dimensions (458x384)
# We want it centered.
padded4 = np.zeros((384, 458, 4), dtype=np.uint8)

y_offset = (384 - new_h) // 2
x_offset = (458 - new_w) // 2

# To make it appear like it's resting on the same spot, 
# we might want to align the bottom edges rather than absolute center.
y_offset = 384 - new_h - 20 # 20 px padding from bottom

# prevent negative offsets
y_offset = max(0, y_offset)
x_offset = max(0, x_offset)

# Copy the resized img4 into the padded canvas
h_to_copy = min(new_h, 384 - y_offset)
w_to_copy = min(new_w, 458 - x_offset)

padded4[y_offset:y_offset+h_to_copy, x_offset:x_offset+w_to_copy] = img4_resized[0:h_to_copy, 0:w_to_copy]

cv2.imwrite('frame_4_fixed.png', padded4)

# Create blends
for i in range(1, 3):
    alpha = i / 3.0
    blend = cv2.addWeighted(img3, 1 - alpha, padded4, alpha, 0)
    cv2.imwrite(f'frame_3_{i}.png', blend)

