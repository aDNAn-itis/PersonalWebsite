# Session Log: Building the Autonomous Animation Studio

## 1. The Core Problem: The "Ballooning" Bug
When generating sequential frames using ChatGPT (DALL-E 3), the AI naturally alters proportions depending on the pose. For example, when the boy sat hunched over in Frame 4, the AI drew him shorter but wider. 
* **Initial failure:** Our first script scaled everything based on *height*. So when the boy hunched, the script stretched his height to match Frame 3, which caused him to "balloon" and look massively fat/wide.
* **The Fix (Area-Scaling):** We scrapped height-scaling and built a "Pixel Volume" calculator using pure Python (`numpy`). We established a constant `TARGET_AREA = 75000` pixels. Now, regardless of the pose, the script mathematically balances the width and height so the character retains the exact same physical volume across all frames!

## 2. The Jitter Bug: Center of Gravity Pinning
* **Initial failure:** We tried pinning the character to the bed using the "bottom center" of their bounding box (their shoes). But because the legs move and stretch differently in every pose, the character jittered wildly.
* **The Fix:** We implemented a literal Center of Mass (CoM) calculator. The script finds the exact center of pixel density and pins *that* coordinate to the bed `(X: 380, Y: 480)`. This instantly grounded the character and made the animation fluid. 

## 3. The Auto-Save Visual Editor (No More Copy-Pasting!)
You had an incredible idea: *"What if we can drag the character around with our mouse in the browser, and it automatically writes the code?"*
* We decoupled the configuration from the Python script into `animatic_config.json`.
* We built a custom backend server (`editor_server.py`).
* We upgraded `preview.html` into a full Drag-and-Drop Editor. When you drag a frame and hit **Save & Rebuild**, the browser talks to the Python backend, instantly updates the JSON config, rebuilds the images, and refreshes the page! 
* *(Bug fix: We had a brief moment where dragging the mouse inverted the math and shot the character into the -712 void, making Frames 2-13 disappear! We fixed the math to `BASE_COM_X + globalDx` and restored them).*

## 4. The Fully Automated Pipeline (aj ghar me panner banga!)
To completely automate the process of adding new frames (like the running scene), we needed a way to strip the white backgrounds from ChatGPT images automatically.
* **Initial failure:** I tried to write a 0-byte OpenCV flood-fill script to save your disk space. It worked, but it left horrible, jagged white halos around the hair because it lacked "alpha matting".
* **The Fix:** We installed a Deep Learning Neural Network called `rembg` (U-Net). It takes up minimal space and uses no GPU, but provides buttery-smooth, anti-aliased edge removal.
* **The Master Script:** We wrote `pipeline.py`. Now, the workflow is:
  1. Generate an image in ChatGPT.
  2. Drop it in `studio/inputs/`.
  3. Run `python3 pipeline.py`.
  4. The script automatically cuts out the background, scales the physical area to 75,000 pixels, aligns the Center of Gravity, and injects it into your live Visual Editor!

## Next Steps for Future Scenes
Because the Area-Scaling logic is 100% universal, this pipeline will work for *any* scene (running, jumping, swimming). The only thing you will ever need to change is dragging the character to their new starting position in the Visual Editor!
