from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets/headphone_connect"
HEADPHONE_PATH = ROOT / "assets/a/headphone_transparent.png"
PHONE_PATH = ROOT / "assets/a/phone_transparent.png"
FINAL_CABLE_PATH = OUT / "cable_final_green.png"

headphone = Image.open(HEADPHONE_PATH).convert("RGBA")
phone = Image.open(PHONE_PATH).convert("RGBA")
generated_cable = Image.open(FINAL_CABLE_PATH).convert("RGBA")
canvas_size = headphone.size


def static_scene():
    """Exact original headphone and phone pixels, in their existing positions."""
    frame = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    frame.alpha_composite(headphone)
    frame.alpha_composite(phone)
    return frame


def extract_generated_cable():
    """Extract the purpose-built cable while preserving its watercolor texture."""
    cable = generated_cable.copy()
    pixels = cable.load()
    for y in range(cable.height):
        for x in range(cable.width):
            r, g, b, a = pixels[x, y]
            strength = g - max(r, b)
            if g > 125 and strength > 25:
                pixels[x, y] = (r, g, b, 0)
            elif g > 90 and strength > 8:
                neutral_green = round((r + b) / 2)
                pixels[x, y] = (r, neutral_green, b, max(0, a - strength * 7))
            elif g > max(r, b) + 2:
                pixels[x, y] = (r, max(r, b) + 2, b, a)
    box = cable.getchannel("A").getbbox()
    cable = cable.crop(box)
    # Fixed endpoint mapping: generated upper-right tip -> loose cable end;
    # generated lower-left tip -> phone's existing top port.
    cable = cable.resize((50, 76), Image.Resampling.LANCZOS)
    # Downscaling collapses the painted cord toward one pixel. Layering the
    # same generated pixels around themselves restores the source cord's
    # three-pixel visual weight without replacing its texture.
    weighted = Image.new("RGBA", (52, 78), (0, 0, 0, 0))
    for offset in ((0, 1), (2, 1), (1, 0), (1, 2), (1, 1)):
        weighted.alpha_composite(cable, offset)
    return weighted


cable_texture = extract_generated_cable()
cable_position = (626, 257)
cable_anchor = (677, 262)

frames = [static_scene()]
reveal_radii = [18, 32, 46, 60, 76, 104]

for radius in reveal_radii:
    frame = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    frame.alpha_composite(headphone)
    visible_cable = cable_texture.copy()
    alpha = visible_cable.getchannel("A")
    for y in range(visible_cable.height):
        for x in range(visible_cable.width):
            scene_x = cable_position[0] + x
            scene_y = cable_position[1] + y
            if (scene_x - cable_anchor[0]) ** 2 + (scene_y - cable_anchor[1]) ** 2 > radius**2:
                alpha.putpixel((x, y), 0)
    visible_cable.putalpha(alpha)
    frame.alpha_composite(visible_cable, cable_position)
    # The phone sits above the cable endpoint, making the contact continuous
    # instead of leaving the cord painted across the phone's face.
    frame.alpha_composite(phone)
    frames.append(frame)

for index, frame in enumerate(frames):
    frame.save(OUT / f"f{index}.png", optimize=True)

print(f"Wrote {len(frames)} exact-scale tangled-cable extension frames")
