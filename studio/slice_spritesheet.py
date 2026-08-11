import cv2
import os
import sys

def slice_spritesheet(img_path, output_dir, num_frames=8):
    if not os.path.exists(img_path):
        print(f"Error: Could not find {img_path}")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    # Load the image
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    h, w = img.shape[:2]
    
    # Calculate the width of a single frame
    frame_width = w // num_frames
    
    print(f"Slicing spritesheet {w}x{h} into {num_frames} frames of {frame_width}x{h}...")
    
    for i in range(num_frames):
        # Slice the region
        start_x = i * frame_width
        end_x = (i + 1) * frame_width
        frame = img[:, start_x:end_x]
        
        out_path = os.path.join(output_dir, f"frame{i}.png")
        cv2.imwrite(out_path, frame)
        print(f"Saved {out_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path to spritesheet image")
    parser.add_argument("frames", type=int, help="Number of frames in the sheet")
    parser.add_argument("--out", default="inputs", help="Output directory")
    args = parser.parse_args()
    
    slice_spritesheet(args.image, args.out, args.frames)
