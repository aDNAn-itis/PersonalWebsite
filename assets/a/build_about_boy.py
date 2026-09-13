from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
NORMAL_GREEN = ASSETS / "a/about_boy_regenerated_green.png"
WINTER_GREEN = ASSETS / "winter_boy/about_boy_regenerated_winter_green.png"
NORMAL_OUT = ASSETS / "a/boy_transparent.png"
WINTER_DIR = ASSETS / "winter_boy"
CANVAS_SIZE = (1080, 723)


def remove_green(path):
    rgb = np.array(Image.open(path).convert("RGB"))
    red = rgb[:, :, 0].astype(np.int16)
    green = rgb[:, :, 1].astype(np.int16)
    blue = rgb[:, :, 2].astype(np.int16)
    excess = green - np.maximum(red, blue)
    alpha = np.clip((110 - excess) * (255 / 75), 0, 255).astype(np.uint8)

    # Neutralize green spill only along partially transparent antialiased edges.
    edge = (alpha > 0) & (alpha < 255)
    rgb[:, :, 1][edge] = np.minimum(
        rgb[:, :, 1][edge], np.maximum(rgb[:, :, 0][edge], rgb[:, :, 2][edge])
    )
    return Image.fromarray(np.dstack((rgb, alpha)), "RGBA")


def fit(source, target_height=273, center_x=470, top=142):
    source = source.crop(source.getchannel("A").getbbox())
    width = round(source.width * target_height / source.height)
    source = source.resize((width, target_height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    canvas.alpha_composite(source, (round(center_x - width / 2), top))
    return canvas


normal = fit(remove_green(NORMAL_GREEN))
winter = fit(remove_green(WINTER_GREEN))
normal.save(NORMAL_OUT, optimize=True)
winter.save(WINTER_DIR / "winter_final.png", optimize=True)

# Match the proven winter animation: identical canvas and smoothstep blending.
for index in range(7):
    progress = index / 6
    eased = progress * progress * (3 - 2 * progress)
    Image.blend(normal, winter, eased).save(WINTER_DIR / f"f{index}.png", optimize=True)

print("Built the relaxed about boy and seven aligned winter frames")
