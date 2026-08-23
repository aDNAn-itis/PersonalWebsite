"""Translate-only lock so a PNG cycle sits on one camera.

    python3 studio/stabilize.py --in assets/scene2 --pattern 'frame*.png'
"""

from __future__ import annotations

import argparse
import glob
import os
import re

import numpy as np
from PIL import Image


def extract_number(path):
    s = re.search(r"\d+", os.path.basename(path))
    return int(s.group()) if s else 0


def content_mask(arr):
    alpha = arr[:, :, 3]
    rgb = arr[:, :, :3]
    return (alpha > 10) & ((rgb[:, :, 0] < 240) | (rgb[:, :, 1] < 240) | (rgb[:, :, 2] < 240))


def clean_speckles(arr, min_col=8, min_row=6):
    mask = content_mask(arr)
    keep = (mask.sum(axis=1) >= min_row)[:, None] & (mask.sum(axis=0) >= min_col)[None, :]
    out = arr.copy()
    out[~keep, 3] = 0
    return out


def fit_canvas(frames):
    """Every frame becomes the same HxW. Smaller files are padded, not stretched."""
    prepared = []
    for frame in frames:
        arr = np.asarray(frame)
        if arr.ndim == 2:
            raise ValueError("Need RGB or RGBA frames")
        if arr.shape[2] == 3:
            rgba = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
            rgba[:, :, :3] = arr
            rgba[:, :, 3] = 255
            arr = rgba
        prepared.append(arr)
    h = max(a.shape[0] for a in prepared)
    w = max(a.shape[1] for a in prepared)
    out = []
    padded = False
    for arr in prepared:
        if arr.shape[0] == h and arr.shape[1] == w:
            out.append(arr)
            continue
        padded = True
        canvas = np.zeros((h, w, 4), dtype=np.uint8)
        canvas[: arr.shape[0], : arr.shape[1]] = arr
        out.append(canvas)
    if padded:
        print(f"stabilize: padded frames to {w}x{h}")
    return out


def shift_canvas(arr, dx, dy):
    dx, dy = int(round(dx)), int(round(dy))
    if dx == 0 and dy == 0:
        return arr
    out = np.zeros_like(arr)
    h, w = arr.shape[:2]
    src_x0, src_y0 = max(0, -dx), max(0, -dy)
    dst_x0, dst_y0 = max(0, dx), max(0, dy)
    src_x1, src_y1 = min(w, w - dx), min(h, h - dy)
    if src_x1 <= src_x0 or src_y1 <= src_y0:
        return out
    out[dst_y0:dst_y0 + (src_y1 - src_y0), dst_x0:dst_x0 + (src_x1 - src_x0)] = arr[src_y0:src_y1, src_x0:src_x1]
    return out


def best_translation(mask, template, max_shift=24):
    ys, xs = np.where(template)
    if len(xs) == 0:
        return 0, 0
    y0 = max(0, int(ys.min()) - max_shift)
    x0 = max(0, int(xs.min()) - max_shift)
    y1 = min(template.shape[0], int(ys.max()) + max_shift + 1)
    x1 = min(template.shape[1], int(xs.max()) + max_shift + 1)
    ref_c = template[y0:y1, x0:x1]
    mask_c = mask[y0:y1, x0:x1]
    h, w = mask_c.shape
    best_s, best_d = -1, (0, 0)
    for dy in range(-max_shift, max_shift + 1):
        for dx in range(-max_shift, max_shift + 1):
            src_x0, src_y0 = max(0, -dx), max(0, -dy)
            dst_x0, dst_y0 = max(0, dx), max(0, dy)
            src_x1, src_y1 = min(w, w - dx), min(h, h - dy)
            if src_x1 <= src_x0 or src_y1 <= src_y0:
                continue
            patch = np.zeros_like(mask_c)
            patch[dst_y0:dst_y0 + (src_y1 - src_y0), dst_x0:dst_x0 + (src_x1 - src_x0)] = (
                mask_c[src_y0:src_y1, src_x0:src_x1]
            )
            score = int(np.count_nonzero(patch & ref_c))
            if score > best_s:
                best_s, best_d = score, (dx, dy)
    return best_d


def occupancy_map(frames):
    return np.stack([content_mask(f) for f in frames], axis=0).sum(axis=0)


def repeating_core(occupancy, n_frames):
    thresh = max(2, int(np.ceil(0.75 * n_frames)))
    core = occupancy >= thresh
    min_px = max(200, 0.08 * float((occupancy > 0).sum()))
    mode = "repeating-core"
    if core.sum() < min_px:
        core = occupancy >= max(2, int(np.ceil(0.5 * n_frames)))
        mode = "majority-core"
    if core.sum() < 200:
        core = occupancy >= 1
        mode = "union-core"
    return core, mode, thresh


def pin_to_core(frames, core, reference, freeze_reference, max_shift):
    """Slide each whole still so it overlaps the repeating object, same ground."""
    ref_shell = content_mask(frames[reference]) & core
    if ref_shell.sum() < 50:
        ref_shell = content_mask(frames[reference])
    ref_foot = int(np.where(ref_shell)[0].max())
    out = []
    for i, frame in enumerate(frames):
        if freeze_reference and i == reference:
            out.append(frame)
            continue
        dx, dy = best_translation(content_mask(frame), core, max_shift=max_shift)
        shifted = shift_canvas(frame, dx, dy)
        shell = content_mask(shifted) & core
        if shell.sum() < 50:
            shell = content_mask(shifted)
        extra_dy = int(round(ref_foot - int(np.where(shell)[0].max())))
        print(f"  frame {i}: core=({dx},{dy}) ground={extra_dy}")
        out.append(shift_canvas(shifted, 0, extra_dy))
    return out


def stabilize_frames(frames, reference=0, max_shift=24, freeze_reference=True, slack=2):
    del slack
    cleaned = [clean_speckles(a) for a in fit_canvas(frames)]
    ref0 = content_mask(cleaned[reference])

    seated = []
    for i, frame in enumerate(cleaned):
        if freeze_reference and i == reference:
            seated.append(frame)
            continue
        dx, dy = best_translation(content_mask(frame), ref0, max_shift=max_shift)
        print(f"  frame {i}: snap=({dx},{dy})")
        seated.append(shift_canvas(frame, dx, dy))

    occupancy = occupancy_map(seated)
    core, mode, thresh = repeating_core(occupancy, len(seated))
    print(f"stabilize: {mode}, {int(core.sum())} anchor pixels, thresh={thresh}/{len(seated)}")
    return pin_to_core(seated, core, reference, freeze_reference, max_shift)


def stabilize_folder(input_dir, output_dir=None, pattern="frame*.png"):
    output_dir = output_dir or input_dir
    os.makedirs(output_dir, exist_ok=True)
    paths = sorted(glob.glob(os.path.join(input_dir, pattern)), key=extract_number)
    if len(paths) < 2:
        raise SystemExit(f"Need at least 2 frames in {input_dir}/{pattern}")
    frames = [np.array(Image.open(p).convert("RGBA")) for p in paths]
    locked = stabilize_frames(frames)
    dest = None
    for path, arr in zip(paths, locked):
        dest = os.path.join(output_dir, os.path.basename(path))
        Image.fromarray(arr).save(dest)
        print(f"wrote {dest} {arr.shape[1]}x{arr.shape[0]}")
    return dest


def consensus_stabilize(canvases, targets):
    """Editor-aware wrapper: lock the sequence, then sit it on the given CoM."""
    locked = stabilize_frames(canvases, freeze_reference=True)
    mask = content_mask(locked[0])
    ys, xs = np.where(mask)
    cx, cy = float(xs.mean()), float(ys.mean())
    base_tx, base_ty = targets[0]
    global_dx = int(round(base_tx - cx))
    global_dy = int(round(base_ty - cy))
    out = []
    for canvas, (tx, ty) in zip(locked, targets):
        extra_dx = int(round(tx - base_tx))
        extra_dy = int(round(ty - base_ty))
        out.append(shift_canvas(canvas, global_dx + extra_dx, global_dy + extra_dy))
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lock a stop-motion PNG sequence so it does not wobble.")
    parser.add_argument("--in", dest="input_dir", required=True)
    parser.add_argument("--out", dest="output_dir", default=None)
    parser.add_argument("--pattern", default="frame*.png")
    args = parser.parse_args()
    stabilize_folder(args.input_dir, args.output_dir, args.pattern)
