from PIL import Image
import numpy as np
import glob
import os

# This script perfectly aligns a sequence of animation frames (like a sprite sheet)
# by finding the center of mass of the character's head and locking it to a fixed coordinate.

def get_head_center(img_path):
    img = Image.open(img_path)
    alpha = np.array(img)[:, :, 3]
    
    # Find bounding box of the non-transparent pixels
    y_nonzero, x_nonzero = np.nonzero(alpha)
    if len(y_nonzero) == 0:
        return 540, 360 # default center if empty
        
    y_min, y_max = np.min(y_nonzero), np.max(y_nonzero)
    x_min, x_max = np.min(x_nonzero), np.max(x_nonzero)
    
    # We only care about the top 20% of the bounding box (the head and shoulders)
    # This prevents moving parts (like legs/pedals) from shifting the center of mass!
    head_y_max = y_min + int((y_max - y_min) * 0.2)
    
    # Get the alpha pixels for just the head area
    head_alpha = alpha[y_min:head_y_max, x_min:x_max]
    
    # Calculate center of mass of the head
    y_head_nonzero, x_head_nonzero = np.nonzero(head_alpha)
    
    if len(x_head_nonzero) == 0:
        return 540, 360
        
    # Global x and y center of the head
    cx = x_min + np.mean(x_head_nonzero)
    cy = y_min + np.mean(y_head_nonzero)
    
    return cx, cy, img

def align_frames():
    files = sorted(glob.glob('assets/b/frame*.png'))
    if not files:
        print("No frames found in assets/b/ directory!")
        return
        
    print(f"Found {len(files)} frames. Aligning...")
    
    # Calculate the target center (let's put the head at exactly X=540, Y=250)
    target_cx = 540
    target_cy = 250

    for f in files:
        try:
            cx, cy, img = get_head_center(f)
            
            # Calculate how far off this frame's head is from the target
            dx = int(target_cx - cx)
            dy = int(target_cy - cy)
            
            img_data = np.array(img)
            shifted_data = np.zeros_like(img_data)
            
            shift_y = dy
            shift_x = dx
            
            # Shift the image data mathematically
            if shift_y > 0:
                src_y_start, src_y_end = 0, img_data.shape[0] - shift_y
                dst_y_start, dst_y_end = shift_y, img_data.shape[0]
            else:
                src_y_start, src_y_end = -shift_y, img_data.shape[0]
                dst_y_start, dst_y_end = 0, img_data.shape[0] + shift_y
                
            if shift_x > 0:
                src_x_start, src_x_end = 0, img_data.shape[1] - shift_x
                dst_x_start, dst_x_end = shift_x, img_data.shape[1]
            else:
                src_x_start, src_x_end = -shift_x, img_data.shape[1]
                dst_x_start, dst_x_end = 0, img_data.shape[1] + shift_x
                
            # Ensure bounds are valid
            src_y_start = max(0, src_y_start)
            src_x_start = max(0, src_x_start)
            dst_y_start = max(0, dst_y_start)
            dst_x_start = max(0, dst_x_start)
            
            # Calculate actual copy sizes
            copy_h = min(src_y_end - src_y_start, dst_y_end - dst_y_start)
            copy_w = min(src_x_end - src_x_start, dst_x_end - dst_x_start)
            
            # Paste the shifted image into the new transparent canvas
            shifted_data[dst_y_start:dst_y_start+copy_h, dst_x_start:dst_x_start+copy_w] = \
                img_data[src_y_start:src_y_start+copy_h, src_x_start:src_x_start+copy_w]
            
            # Overwrite the original frame with the perfectly aligned one
            Image.fromarray(shifted_data).save(f)
            print(f"Aligned {os.path.basename(f)}: shifted by X:{dx}, Y:{dy}")
            
        except Exception as e:
            print(f"Error on {f}: {e}")

    print("Head alignment complete! All frames are perfectly synchronized.")

if __name__ == "__main__":
    align_frames()
