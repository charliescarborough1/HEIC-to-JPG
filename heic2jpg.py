#!/usr/bin/env python3
"""
Convert HEIC/HEIF images to JPEG.

Install deps:
    pip install pillow pillow-heif

Usage:
    python heic2jpg.py photo.heic
    python heic2jpg.py ~/Pictures/iphone_dump -o ~/Pictures/converted
    python heic2jpg.py ~/Pictures -r -q 90 --delete-originals
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps
import pillow_heif

pillow_heif.register_heif_opener()

HEIC_EXTS = {".heic", ".heif", ".hif"}


def convert(src: Path, dst: Path, quality: int, overwrite: bool) -> bool:
    if dst.exists() and not overwrite:
        print(f"skip (exists): {dst.name}")
        return False

    with Image.open(src) as im:
        # Honor the EXIF orientation tag, then drop it so the pixels aren't
        # rotated twice by viewers that also read the tag.
        im = ImageOps.exif_transpose(im)

        exif = im.info.get("exif")

        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")

        dst.parent.mkdir(parents=True, exist_ok=True)
        save_kwargs = {
            "quality": quality,
            "optimize": True,
            # 0 = 4:4:4 (no chroma subsampling), 2 = 4:2:0. Do NOT use "keep"
            # here -- Pillow only allows it when the source is already a JPEG.
            "subsampling": 0 if quality >= 90 else 2,
        }
        if exif:
            save_kwargs["exif"] = exif

        im.save(dst, "JPEG", **save_kwargs)

    return True


def collect(target: Path, recursive: bool):
    if target.is_file():
        return [target]
    pattern = "**/*" if recursive else "*"
    return sorted(
        p for p in target.glob(pattern)
        if p.is_file() and p.suffix.lower() in HEIC_EXTS
    )


def main():
    ap = argparse.ArgumentParser(description="Convert HEIC/HEIF images to JPEG.")
    ap.add_argument("input", type=Path, help="HEIC file or a directory of them")
    ap.add_argument("-o", "--output", type=Path,
                    help="output directory (default: alongside the originals)")
    ap.add_argument("-q", "--quality", type=int, default=95,
                    help="JPEG quality 1-95 (default: 95)")
    ap.add_argument("-r", "--recursive", action="store_true",
                    help="recurse into subdirectories")
    ap.add_argument("--overwrite", action="store_true",
                    help="overwrite existing .jpg files")
    ap.add_argument("--delete-originals", action="store_true",
                    help="delete each HEIC after a successful conversion")
    args = ap.parse_args()

    if not args.input.exists():
        sys.exit(f"No such path: {args.input}")

    files = collect(args.input, args.recursive)
    if not files:
        sys.exit("No HEIC/HEIF files found.")

    base = args.input if args.input.is_dir() else args.input.parent
    converted = failed = 0

    for src in files:
        if args.output:
            rel = src.relative_to(base) if args.input.is_dir() else Path(src.name)
            dst = args.output / rel.with_suffix(".jpg")
        else:
            dst = src.with_suffix(".jpg")

        try:
            if convert(src, dst, args.quality, args.overwrite):
                converted += 1
                print(f"{src.name} -> {dst}")
                if args.delete_originals:
                    src.unlink()
        except Exception as e:
            failed += 1
            print(f"FAILED {src.name}: {e}", file=sys.stderr)

    print(f"\nDone. {converted} converted, {failed} failed, {len(files)} found.")


if __name__ == "__main__":
    main()
