#!/usr/bin/env python3
"""Prepare a photo for ASCII conversion.

Removes the background, lifts local contrast, and composites onto pure white so
the background maps to the blank end of the ASCII ramp.

Usage: python scripts/prep_photo.py source-photo.jpg
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps


def remove_background(img: Image.Image) -> Image.Image:
    """Remove the subject's background with rembg, falling back to colour keying.

    A busy background (a mural, a street) defeats a border-colour key, so the
    segmentation model is tried first. The fallback still works for studio
    photos with a flat backdrop.
    """
    try:
        from rembg import remove as rembg_remove

        cut = rembg_remove(img)
        out = Image.new("RGBA", img.size, (255, 255, 255, 255))
        out.paste(cut, (0, 0), cut)
        return out.convert("RGB")
    except Exception as exc:  # pragma: no cover - depends on local model
        print(f"rembg unavailable ({exc}); falling back to colour keying")

    rgb = np.asarray(img.convert("RGB")).astype(np.float32)
    h, w, _ = rgb.shape

    border = np.concatenate(
        [rgb[0, :, :], rgb[-1, :, :], rgb[:, 0, :], rgb[:, -1, :]], axis=0
    )
    bg = np.median(border, axis=0)

    dist = np.linalg.norm(rgb - bg, axis=2)
    # Anything close to the border colour is background. The soft ramp keeps
    # hair and shoulders from turning into a hard cut-out.
    lo, hi = 26.0, 78.0
    alpha = np.clip((dist - lo) / (hi - lo), 0.0, 1.0)

    alpha_img = Image.fromarray((alpha * 255).astype(np.uint8), "L")
    alpha_img = alpha_img.filter(ImageFilter.GaussianBlur(1.2))

    out = Image.new("RGBA", img.size, (255, 255, 255, 255))
    out.paste(img.convert("RGB"), (0, 0), alpha_img)
    return out.convert("RGB")


def boost_contrast(img: Image.Image) -> Image.Image:
    """Approximate CLAHE with autocontrast plus a local unsharp pass."""
    gray = ImageOps.grayscale(img)
    gray = ImageOps.autocontrast(gray, cutoff=1)

    arr = np.asarray(gray).astype(np.float32)
    blurred = np.asarray(gray.filter(ImageFilter.GaussianBlur(9))).astype(np.float32)
    # Local contrast: push each pixel away from its neighbourhood mean.
    local = arr + 1.15 * (arr - blurred)
    local = np.clip(local, 0, 255).astype(np.uint8)

    out = Image.fromarray(local, "L")
    return ImageOps.autocontrast(out, cutoff=0)



def crop_to_subject(img: Image.Image) -> Image.Image:
    """Crop to the subject and keep the head and upper chest.

    The cut-out has a white background, so a difference from white gives a
    usable bounding box without needing the alpha channel back.
    """
    arr = np.asarray(img.convert("L")).astype(np.int16)
    mask = (255 - arr) > 18
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return img

    x0, x1 = xs.min(), xs.max()
    y0, y1 = ys.min(), ys.max()
    w = x1 - x0
    h = y1 - y0

    # Keep the upper part of the subject: head plus a little chest.
    keep_h = int(h * 0.78)
    cx = (x0 + x1) // 2
    side = int(max(w, keep_h) * 1.02)
    left = max(0, cx - side // 2)
    top = max(0, y0 - int(h * 0.02))
    right = min(img.width, left + side)
    bottom = min(img.height, top + side)
    return img.crop((left, top, right, bottom))

def main() -> None:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg")
    if not src.exists():
        raise SystemExit(f"photo not found: {src}")

    img = Image.open(src).convert("RGB")
    # Keep the working image small; the ASCII grid is ~100 cells wide.
    img.thumbnail((900, 900), Image.LANCZOS)

    img = remove_background(img)
    img = crop_to_subject(img)
    img = boost_contrast(img)

    # A slight blur before downsampling avoids single-pixel noise becoming
    # random glyphs in the output.
    img = img.filter(ImageFilter.GaussianBlur(0.6))

    img.save("source-prepped.png")
    print(f"wrote source-prepped.png ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
