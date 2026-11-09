# HEIC to JPEG Converter

`heic2jpg.py` converts a single HEIC image or a folder of HEIC/HEIF images to `.jpg` files. Folder scans recognize `.heic`, `.heif`, and `.hif` extensions regardless of case.

## Setup

Run these commands from the folder containing `heic2jpg.py`:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install Pillow pillow-heif
```

## Usage

Convert one image. This saves `photo.jpg` beside `photo.heic`.

```sh
python heic2jpg.py photo.heic
```

Convert a folder and its subfolders, preserving their structure under `converted/`.

```sh
python heic2jpg.py "iPhone Photos" --recursive --output converted --quality 90
```

## Options

| Option | Behavior |
| --- | --- |
| `-o DIR`, `--output DIR` | Save JPEGs under `DIR`. By default, each JPEG goes beside its source. |
| `-q N`, `--quality N` | Set JPEG quality from 1 to 95. Defaults to 95. |
| `-r`, `--recursive` | Include subfolders when the input is a directory. |
| `--overwrite` | Replace existing JPEGs. By default, the script skips them. |
| `--delete-originals` | Delete each source image after its JPEG is saved. Skipped files and failed conversions keep their originals. |
| `-h`, `--help` | Show command-line help. |

The converter applies EXIF orientation to the image pixels and carries over available EXIF metadata after the orientation adjustment. During a batch, it reports each conversion, skip, or error and prints totals at the end.
