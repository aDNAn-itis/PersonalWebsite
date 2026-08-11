import cv2
import numpy as np
import os
import glob
import re
import json

def extract_number(f):
    s = re.search(r'\d+', os.path.basename(f))
    return int(s.group()) if s else 0

def warp_image(img, flow):
    h, w = flow.shape[:2]
    # Create coordinate grid
    y, x = np.mgrid[0:h, 0:w].reshape(2, -1)
    
    fx = flow[:,:,0].flatten()
    fy = flow[:,:,1].flatten()
    
    map_x = (x - fx).astype(np.float32).reshape(h, w)
    map_y = (y - fy).astype(np.float32).reshape(h, w)
    
    return cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)

def update_preview_html(output_dir, frame_count, fps):
    # Rewrite the preview.html to use the new interpolated frames
    html_path = 'preview.html'
    
    if not os.path.exists(html_path):
        return
        
    with open(html_path, 'r') as f:
        content = f.read()
        
    frames_list = [f"{output_dir}/inter_{i:03d}.png" for i in range(frame_count)]
    
    new_content = re.sub(
        r'const frames = \[[^\]]*\];',
        f'const frames = {json.dumps(frames_list)};',
        content
    )
    
    new_content = re.sub(
        r'setTimeout\(loop, 1000 / \d+\);',
        f'setTimeout(loop, 1000 / {fps});',
        new_content
    )
    
    with open(html_path, 'w') as f:
        f.write(new_content)
    print(f"Updated preview.html to play {fps} FPS Interpolated Animation!")

def interpolate_frames(input_dir, output_dir, steps=3):
    os.makedirs(output_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(input_dir, 'frame*.png')), key=extract_number)
    
    if len(files) < 2:
        print("Not enough frames to interpolate.")
        return
        
    out_idx = 0
    print(f"Reverting to Farneback Optical Flow (CPU) with {steps} intermediate steps...")
    
    for i in range(len(files) - 1):
        img1 = cv2.imread(files[i], cv2.IMREAD_UNCHANGED)
        cv2.imwrite(os.path.join(output_dir, f'inter_{out_idx:03d}.png'), img1)
        out_idx += 1
        
        img2 = cv2.imread(files[i+1], cv2.IMREAD_UNCHANGED)
        gray1 = cv2.cvtColor(img1[:,:,:3], cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2[:,:,:3], cv2.COLOR_BGR2GRAY)
        
        flow_forward = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        flow_backward = cv2.calcOpticalFlowFarneback(gray2, gray1, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        
        for step in range(1, steps + 1):
            t = step / (steps + 1)
            warp1 = warp_image(img1, flow_forward * t)
            warp2 = warp_image(img2, flow_backward * (1 - t))
            blend = cv2.addWeighted(warp1, 1 - t, warp2, t, 0)
            cv2.imwrite(os.path.join(output_dir, f'inter_{out_idx:03d}.png'), blend)
            out_idx += 1
            
        print(f"Interpolated between frame {i} and {i+1}")

    # Loop back transition
    last_img = cv2.imread(files[-1], cv2.IMREAD_UNCHANGED)
    cv2.imwrite(os.path.join(output_dir, f'inter_{out_idx:03d}.png'), last_img)
    out_idx += 1
    
    img_first = cv2.imread(files[0], cv2.IMREAD_UNCHANGED)
    gray1 = cv2.cvtColor(last_img[:,:,:3], cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img_first[:,:,:3], cv2.COLOR_BGR2GRAY)
    
    flow_forward = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    flow_backward = cv2.calcOpticalFlowFarneback(gray2, gray1, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    
    for step in range(1, steps + 1):
        t = step / (steps + 1)
        warp1 = warp_image(last_img, flow_forward * t)
        warp2 = warp_image(img_first, flow_backward * (1 - t))
        blend = cv2.addWeighted(warp1, 1 - t, warp2, t, 0)
        cv2.imwrite(os.path.join(output_dir, f'inter_{out_idx:03d}.png'), blend)
        out_idx += 1
    
    print(f"\\nInterpolation complete! Generated {out_idx} total frames in '{output_dir}'.")
    
    # Base fps is 6. With `steps` intermediates, we have (steps + 1) * 6 fps.
    fps = (steps + 1) * 6
    update_preview_html(output_dir, out_idx, fps)

if __name__ == "__main__":
    interpolate_frames("aligned_frames", "interpolated_frames", steps=3)
