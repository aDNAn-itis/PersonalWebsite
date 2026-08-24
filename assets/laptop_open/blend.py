import cv2
import numpy as np
import sys

img1 = cv2.imread('frame_3.png', cv2.IMREAD_UNCHANGED)
img2 = cv2.imread('frame_4.png', cv2.IMREAD_UNCHANGED)

# Ensure same size for blending
h = max(img1.shape[0], img2.shape[0])
w = max(img1.shape[1], img2.shape[1])

def pad_to_size(img, h, w):
    pad_h = (h - img.shape[0]) // 2
    pad_w = (w - img.shape[1]) // 2
    padded = np.zeros((h, w, 4), dtype=np.uint8)
    padded[pad_h:pad_h+img.shape[0], pad_w:pad_w+img.shape[1]] = img
    return padded

img1 = pad_to_size(img1, h, w)
img2 = pad_to_size(img2, h, w)

# We will create 2 intermediate frames
for i in range(1, 3):
    alpha = i / 3.0
    blend = cv2.addWeighted(img1, 1 - alpha, img2, alpha, 0)
    cv2.imwrite(f'frame_3_{i}.png', blend)

