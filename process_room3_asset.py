from pathlib import Path

import numpy as np
from PIL import Image


source = Path(
    "/home/adnan/.codex/generated_images/01a053c1-4d1e-74a2-bc90-2d204e9dd786/"
    "exec-91b89609-85a0-439a-abf9-d8971a56da23.png"
)
output_dir = Path("assets/rooms/room3")
output_dir.mkdir(parents=True, exist_ok=True)

image = Image.open(source).convert("RGBA")
pixels = np.array(image)
rgb = pixels[..., :3]

# Remove the generated transparency-preview checker while preserving the warm
# wood, cream chalk, slate texture, and hand-painted edge softness.
neutral = rgb.max(axis=2) - rgb.min(axis=2) < 7
bright = rgb.min(axis=2) > 226
pixels[..., 3][neutral & bright] = 0

Image.fromarray(pixels).save(output_dir / "blackboard.png")
print(f"Saved {output_dir / 'blackboard.png'}")
