from pathlib import Path
from PIL import Image
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets/grass_relax"

seated_source = Image.open(ROOT / "assets/a/boy_transparent.png").convert("RGBA")


def fit_image(source, target_height=430, center_x=490, top=116, crop_box=None):
    source = source.convert("RGBA")
    source = source.crop(crop_box or source.getchannel("A").getbbox())
    width = round(source.width * target_height / source.height)
    source = source.resize((width, target_height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", seated_source.size, (0, 0, 0, 0))
    canvas.alpha_composite(source, (round(center_x - width / 2), top))
    return canvas


def remove_chroma_green(source_name, output_name):
    image = np.array(Image.open(OUT / source_name).convert("RGB"))
    red = image[:, :, 0].astype(np.int16)
    green = image[:, :, 1].astype(np.int16)
    blue = image[:, :, 2].astype(np.int16)
    green_excess = green - np.maximum(red, blue)
    alpha = np.clip((105 - green_excess) * (255 / 70), 0, 255).astype(np.uint8)
    rgba = np.dstack((image, alpha))
    cutout = Image.fromarray(rgba, "RGBA")
    cutout.save(OUT / output_name, optimize=True)
    return cutout


bridge_one = remove_chroma_green("bridge-pose-1-green.png", "bridge-pose-1-cutout.png")
bridge_two = remove_chroma_green("bridge-pose-2-green.png", "bridge-pose-2-cutout.png")

# Real pose progression from the compact about pose into the relaxed pose.
keyframes = [
    seated_source,
    fit_image(bridge_one),
    fit_image(bridge_two),
    fit_image(Image.open(OUT / "transition-2-cutout.png")),
    fit_image(Image.open(OUT / "replacement-2-cutout.png")),
    fit_image(Image.open(OUT / "transition-3-cutout.png")),
    fit_image(Image.open(OUT / "relaxed_boy-cutout.png")),
]

for index, frame in enumerate(keyframes):
    frame.save(OUT / f"f{index}.png", optimize=True)

keyframes[-1].save(OUT / "relaxed_boy-fitted.png", optimize=True)
print(f"Wrote {len(keyframes)} genuine seated-to-relaxed pose frames")
