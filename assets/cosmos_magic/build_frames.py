from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets/a/books_transparent.png"
SHEET = ROOT / "assets/cosmos_magic/source_sheet.png"
OUT = ROOT / "assets/cosmos_magic"

source = Image.open(SOURCE).convert("RGBA")
sheet = Image.open(SHEET).convert("RGBA")
canvas_size = source.size


def exact_polygon_layer(points):
    mask = Image.new("L", canvas_size, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    layer = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    layer.paste(source, (0, 0), mask)
    return layer


# Preserve the lower purple book using its original pixels. The closed Cosmos
# cover is deliberately excluded so it cannot remain beneath the opening pages.
purple_book = exact_polygon_layer(
    [(58, 432), (102, 413), (123, 435), (107, 509), (90, 513), (63, 449)]
)


# Cell zero is deliberately unused. Frame zero is the exact original asset;
# later frames replace its Cosmos cover while retaining the lower book.
cells = [
    (233, 302, 463, 640),
    (469, 302, 703, 640),
    (709, 302, 943, 640),
    (950, 302, 1180, 640),
    (1186, 302, 1422, 640),
    (1428, 302, 1668, 640),
]


def remove_green(image):
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if g > 145 and g > r * 1.28 and g > b * 1.28:
                pixels[x, y] = (r, g, b, 0)
    return image


def normalized_book(cell):
    cutout = remove_green(sheet.crop(cell))
    alpha_box = cutout.getchannel("A").getbbox()
    if alpha_box:
        cutout = cutout.crop(alpha_box)

    cutout = cutout.rotate(-7, resample=Image.Resampling.BICUBIC, expand=True)
    rotated_alpha_box = cutout.getchannel("A").getbbox()
    if rotated_alpha_box:
        cutout = cutout.crop(rotated_alpha_box)
    # Keep one physical scale across the whole animation. Using thumbnail()
    # with separate width/height limits made portrait and landscape stages
    # shrink by different amounts, so the book appeared to change size.
    target_long_edge = 124
    scale = target_long_edge / max(cutout.width, cutout.height)
    cutout = cutout.resize(
        (round(cutout.width * scale), round(cutout.height * scale)),
        Image.Resampling.LANCZOS,
    )
    return cutout


frames = [source.copy()]
anchor = (151, 484)

for cell in cells:
    book = normalized_book(cell)
    frame = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    x = round(anchor[0] - book.width / 2)
    y = round(anchor[1] - book.height / 2)
    frame.alpha_composite(purple_book)
    frame.alpha_composite(book, (x, y))
    frames.append(frame)

for index, frame in enumerate(frames):
    frame.save(OUT / f"f{index}.png", optimize=True)

print(f"Wrote {len(frames)} replacement frames with an exact static frame zero")
