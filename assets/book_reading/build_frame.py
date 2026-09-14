from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
CANVAS_SIZE = (1080, 723)

def remove_green_spill(image):
    pixels = np.array(image.convert("RGBA"))
    red = pixels[:, :, 0].astype(np.int16)
    green = pixels[:, :, 1].astype(np.int16)
    blue = pixels[:, :, 2].astype(np.int16)
    excess = green - np.maximum(red, blue)
    chroma_alpha = np.clip((55 - excess) * (255 / 45), 0, 255).astype(np.uint8)
    pixels[:, :, 3] = np.minimum(pixels[:, :, 3], chroma_alpha)
    edge = pixels[:, :, 3] < 250
    pixels[:, :, 1][edge] = np.minimum(
        pixels[:, :, 1][edge],
        np.maximum(pixels[:, :, 0][edge], pixels[:, :, 2][edge]) + 6,
    )
    return Image.fromarray(pixels, "RGBA")


for source_name, output_name in (
    ("transition-1-cutout.png", "transition-1-fitted.png"),
    ("transition-2-cutout.png", "transition-2-fitted.png"),
    ("reading-boy-cutout.png", "reading-boy-fitted.png"),
):
    source = remove_green_spill(Image.open(HERE / source_name))
    source = source.crop(source.getchannel("A").getbbox())
    target_height = 430
    target_width = round(source.width * target_height / source.height)
    source = source.resize((target_width, target_height), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    canvas.alpha_composite(source, (round(490 - target_width / 2), 116))
    canvas.save(HERE / output_name, optimize=True)

print("Wrote three aligned Sakura reading frames")
