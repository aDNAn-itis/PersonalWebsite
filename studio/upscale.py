import cv2
import glob
import os

def upscale_image(img_path, scale_factor=2):
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None: 
        print(f"Failed to load {img_path}")
        return
    
    # Handle alpha channel
    has_alpha = img.shape[2] == 4
    if has_alpha:
        bgr = img[:, :, :3]
        alpha = img[:, :, 3]
    else:
        bgr = img
        alpha = None
        
    # Upscale using Lanczos4 (best for preserving details on pixelated images)
    h, w = bgr.shape[:2]
    bgr_up = cv2.resize(bgr, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_LANCZOS4)
    
    # Apply Bilateral Filter to smooth out compression artifacts while preserving edges
    bgr_smooth = cv2.bilateralFilter(bgr_up, d=9, sigmaColor=75, sigmaSpace=75)
    
    # Sharpen the image slightly to pop the character lines
    bgr_sharp = cv2.detailEnhance(bgr_smooth, sigma_s=10, sigma_r=0.15)
    
    if has_alpha:
        alpha_up = cv2.resize(alpha, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_LANCZOS4)
        # Threshold the alpha to keep the edges clean
        _, alpha_up = cv2.threshold(alpha_up, 127, 255, cv2.THRESH_BINARY)
        result = cv2.merge([bgr_sharp[:,:,0], bgr_sharp[:,:,1], bgr_sharp[:,:,2], alpha_up])
    else:
        result = bgr_sharp
        
    cv2.imwrite(img_path, result)
    print(f"Upscaled & Enhanced: {os.path.basename(img_path)} (New size: {w*scale_factor}x{h*scale_factor})")

print("Starting AI-Math Upscaling Pipeline...")
for f in glob.glob("inputs/*.png"):
    upscale_image(f)
print("Done! Ready for background removal.")
