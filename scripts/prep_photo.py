#!/usr/bin/env python3
"""Prepare the GitHub avatar for ASCII conversion.

Removes the background, crops to the subject, and writes two files:

  source-prepped.png        grayscale, contrast-lifted, used for glyph choice
  source-prepped-color.png  colour crop, used to find the gold glasses

Usage: python scripts/prep_photo.py [source-avatar.png]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps


def remove_background(img: Image.Image) -> Image.Image:
    """Cut the subject out with rembg, falling back to a border colour key."""
    try:
        from rembg import remove as rembg_remove

        cut = rembg_remove(img)
        out = Image.new("RGBA", img.size, (255, 255, 255, 255))
        out.paste(cut, (0, 0), cut)
        return out.convert("RGB")
    except Exception as exc:  # pragma: no cover - depends on local model
        print(f"rembg unavailable ({exc}); falling back to colour keying")

    rgb = np.asarray(img.convert("RGB")).astype(np.float32)
    border = np.concatenate(
        [rgb[0, :, :], rgb[-1, :, :], rgb[:, 0, :], rgb[:, -1, :]], axis=0
    )
    bg = np.median(border, axis=0)
    dist = np.linalg.norm(rgb - bg, axis=2)
    alpha = np.clip((dist - 26.0) / (78.0 - 26.0), 0.0, 1.0)
    alpha_img = Image.fromarray((alpha * 255).astype(np.uint8), "L")
    alpha_img = alpha_img.filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new("RGBA", img.size, (255, 255, 255, 255))
    out.paste(img.convert("RGB"), (0, 0), alpha_img)
    return out.convert("RGB")


def crop_to_subject(img: Image.Image) -> Image.Image:
    """Crop to the subject, keeping the head and a little chest."""
    arr = np.asarray(img.convert("L")).astype(np.int16)
    mask = (255 - arr) > 18
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return img

    x0, x1 = xs.min(), xs.max()
    y0, y1 = ys.min(), ys.max()
    w, h = x1 - x0, y1 - y0

    keep_h = int(h * 0.80)
    cx = (x0 + x1) // 2
    side = int(max(w, keep_h) * 1.02)
    left = max(0, cx - side // 2)
    top = max(0, y0 - int(h * 0.02))
    right = min(img.width, left + side)
    bottom = min(img.height, top + side)
    return img.crop((left, top, right, bottom))


def boost_contrast(img: Image.Image) -> Image.Image:
    """Lift local contrast so the face reads in a coarse character grid."""
    gray = ImageOps.grayscale(img)
    gray = ImageOps.autocontrast(gray, cutoff=1)

    arr = np.asarray(gray).astype(np.float32)
    blurred = np.asarray(gray.filter(ImageFilter.GaussianBlur(7))).astype(np.float32)
    local = arr + 1.5 * (arr - blurred)
    local = np.clip(local, 0, 255).astype(np.uint8)

    out = Image.fromarray(local, "L")

    # Histogram equalisation spreads the tones the subject actually uses, which
    # is what makes a dark statue readable in a coarse grid. Apply it inside the
    # subject only: equalising the whole frame turns the white backdrop grey and
    # fills the background with glyphs.
    equalised = ImageOps.equalize(out)
    arr_eq = np.asarray(equalised).astype(np.float32)
    arr_out = np.asarray(out).astype(np.float32)
    subject = arr_out < 244
    blended = np.where(subject, arr_eq, 255.0)

    return Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8), "L")


def main() -> None:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "source-avatar.png")
    if not src.exists():
        raise SystemExit(f"avatar not found: {src}")

    img = Image.open(src).convert("RGB")
    img.thumbnail((900, 900), Image.LANCZOS)

    img = remove_background(img)
    img = crop_to_subject(img)
    img.save("source-prepped-color.png")

    gray = boost_contrast(img)
    gray = gray.filter(ImageFilter.GaussianBlur(0.5))
    gray.save("source-prepped.png")

    print(f"wrote source-prepped.png and source-prepped-color.png ({gray.width}x{gray.height})")


if __name__ == "__main__":
    main()
