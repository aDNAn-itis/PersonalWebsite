from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
RELAXED = ROOT / "assets/grass_relax/relaxed_boy-cutout.png"
RELAXED_RESTORED = ROOT / "assets/grass_relax/relaxed_boy-rembg.png"
WINTER_DIR = ROOT / "assets/winter_boy"
TRANSITION_THREE = ROOT / "assets/grass_relax/transition-3-cutout.png"
TRANSITION_THREE_RESTORED = ROOT / "assets/grass_relax/transition-3-rembg.png"
REPLACEMENT_THREE = ROOT / "assets/grass_relax/replacement-3-cutout.png"
REPLACEMENT_THREE_CLEAN = ROOT / "assets/grass_relax/replacement-3-clean.png"


def clear_enclosed_checkerboard():
    image = np.array(Image.open(RELAXED_RESTORED).convert("RGBA"))
    rgb = image[:, :, :3]
    alpha = image[:, :, 3]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    ink_barrier = cv2.dilate((gray < 90).astype(np.uint8), np.ones((3, 3), np.uint8), 1)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(1 - ink_barrier, 8)
    holes = np.zeros_like(alpha, dtype=np.uint8)
    for label in range(1, count):
        x, y, width, height, area = stats[label]
        is_arm_opening = (
            560 < x < 790 and 150 < y < 245 and
            90 < width < 130 and 45 < height < 90 and area > 1500
        )
        if is_arm_opening:
            holes[labels == label] = 255

    holes = cv2.dilate(holes, np.ones((3, 3), np.uint8), iterations=2)
    holes = cv2.GaussianBlur(holes, (0, 0), 0.6)
    alpha = np.minimum(alpha, 255 - holes)

    image[:, :, 3] = alpha
    Image.fromarray(image, "RGBA").save(RELAXED, optimize=True)


def sharpen_winter_final():
    for name in ("winter_final.png", "f6.png"):
        path = WINTER_DIR / name
        image = Image.open(path).convert("RGBA")
        red, green, blue, alpha = image.split()
        rgb = Image.merge("RGB", (red, green, blue)).filter(
            ImageFilter.UnsharpMask(radius=0.85, percent=165, threshold=2)
        )
        sharpened = Image.merge("RGBA", (*rgb.split(), alpha))
        sharpened.save(path, optimize=True)


def clear_transition_three_checkerboard():
    image = np.array(Image.open(TRANSITION_THREE_RESTORED).convert("RGBA"))
    rgb = image[:, :, :3]
    alpha = image[:, :, 3]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    ink_barrier = cv2.dilate((gray < 105).astype(np.uint8), np.ones((3, 3), np.uint8), 1)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(1 - ink_barrier, 8)
    holes = np.zeros_like(alpha, dtype=np.uint8)
    for label in range(1, count):
        x, y, width, height, area = stats[label]
        is_arm_opening = (
            565 < x < 590 and 190 < y < 215 and
            95 < width < 120 and 55 < height < 80 and area > 1400
        )
        if is_arm_opening:
            holes[labels == label] = 255
    holes = cv2.dilate(holes, np.ones((3, 3), np.uint8), iterations=2)
    holes = cv2.GaussianBlur(holes, (0, 0), 0.6)
    image[:, :, 3] = np.minimum(alpha, 255 - holes)
    Image.fromarray(image, "RGBA").save(TRANSITION_THREE, optimize=True)


def clear_replacement_three_checkerboard():
    image = np.array(Image.open(REPLACEMENT_THREE).convert("RGBA"))
    rgb = image[:, :, :3]
    alpha = image[:, :, 3]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    ink_barrier = cv2.dilate((gray < 100).astype(np.uint8), np.ones((3, 3), np.uint8), 1)
    holes = np.zeros_like(alpha, dtype=np.uint8)

    # The source also contains a large checkerboard island enclosed by the
    # head, raised arm and shirt.  It is made up of disconnected light/dark
    # squares, so connected-component matching alone cannot select it. Limit
    # the colour selection to that opening to protect the boy and headphones.
    opening = np.zeros_like(alpha, dtype=np.uint8)
    cv2.fillPoly(
        opening,
        [np.array([
            [750, 58], [790, 54], [842, 82], [884, 123], [930, 169],
            [982, 213], [958, 239], [895, 247], [826, 250], [765, 242],
            [750, 218], [750, 172],
        ], dtype=np.int32)],
        255,
    )
    # Keep the complete right ear cup while clearing the background around it.
    cv2.ellipse(opening, (776, 178), (22, 49), 0, 0, 360, 0, -1)
    channel_spread = rgb.max(axis=2).astype(np.int16) - rgb.min(axis=2).astype(np.int16)
    brightness = rgb.max(axis=2)
    checker_pixels = (
        (opening > 0) &
        (channel_spread < 14) &
        (brightness > 0) &
        (brightness < 190)
    )
    checker = (checker_pixels.astype(np.uint8) * 255)
    checker = cv2.morphologyEx(
        checker, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=1
    )
    holes = np.maximum(holes, checker)
    left_gap = np.zeros_like(alpha, dtype=np.uint8)
    cv2.fillPoly(
        left_gap,
        [np.array([
            [574, 201], [609, 191], [640, 207],
            [642, 232], [624, 243], [591, 235],
        ], dtype=np.int32)],
        255,
    )
    holes = np.maximum(holes, left_gap)
    holes = cv2.GaussianBlur(holes, (0, 0), 0.6)
    image[:, :, 3] = np.minimum(alpha, 255 - holes)
    Image.fromarray(image, "RGBA").save(REPLACEMENT_THREE_CLEAN, optimize=True)


clear_enclosed_checkerboard()
clear_transition_three_checkerboard()
clear_replacement_three_checkerboard()
print("Cleaned enclosed backgrounds in replacement frame 3 and final pose")
