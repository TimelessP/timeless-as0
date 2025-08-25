#!/usr/bin/env python3
"""
Map Gray Earth Fetch Tool for Airship Zero

Downloads Natural Earth Gray Earth (elevation/grayscale) raster and
produces a game-ready grayscale PNG heightmap at:

  assets/png/world-heightmap.png

The script also computes simple stats (min, sea-level estimate, max)
and writes them to the README in `doc/MAP_GRAY_FETCH_README.md`.

This is a development tool. Natural Earth data is public domain.
"""
from pathlib import Path
import os
import sys
import urllib.request
import urllib.error
import zipfile
import shutil
import tempfile

# Optional dependencies
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except Exception:
    NUMPY_AVAILABLE = False

# Natural Earth Gray Earth URL (use medium-resolution Gray LR SR which is known to download)
NATURAL_EARTH_BASE_URL = "https://naciscdn.org/naturalearth"
# Use the medium-resolution Gray Earth with Shaded Relief (LR = low/medium res)
GRAY_EARTH_URL = f"{NATURAL_EARTH_BASE_URL}/10m/raster/GRAY_LR_SR.zip"


def download_file(url: str, dest_path: Path) -> bool:
    try:
        print(f"Downloading {url}...")
        # Use a browser-like User-Agent to avoid simple CDN blocks
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; AirshipZero/1.0)"})
        with urllib.request.urlopen(req, timeout=60) as response, open(dest_path, 'wb') as out:
            shutil.copyfileobj(response, out)
        return True
    except urllib.error.HTTPError as e:
        print(f"Error downloading {url}: {e}")
        # If CDN blocks simple clients (403), try requests if available
        if e.code == 403:
            try:
                import requests
            except Exception:
                print("'requests' not installed; cannot retry with requests library")
                return False
            try:
                print("Retrying with requests and a browser User-Agent...")
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                with requests.get(url, headers=headers, stream=True, timeout=60) as r:
                    if r.status_code == 200:
                        with open(dest_path, 'wb') as out:
                            for chunk in r.iter_content(8192):
                                if chunk:
                                    out.write(chunk)
                        return True
                    else:
                        print(f"Requests retry failed: HTTP {r.status_code}")
                        return False
            except Exception as e2:
                print(f"Requests retry error: {e2}")
                return False
        return False
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


def extract_zip(zip_path: Path, extract_dir: Path) -> bool:
    try:
        print(f"Extracting {zip_path.name}...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_dir)
        return True
    except Exception as e:
        print(f"Error extracting {zip_path}: {e}")
        return False


def find_tif_file(directory: Path) -> Path:
    tif_files = list(directory.rglob("*.tif"))
    if not tif_files:
        raise FileNotFoundError("No .tif files found in extracted directory")
    # Prefer filenames that look like GRAY or similar
    for f in tif_files:
        if "GRAY" in f.name.upper():
            return f
    # Fallback to largest
    return max(tif_files, key=lambda f: f.stat().st_size)


def convert_tif_to_png_pillow(tif_path: Path, png_path: Path, target_size=(1536, 1024)) -> bool:
    if not PIL_AVAILABLE:
        print("Pillow not available")
        return False
    try:
        print(f"Opening TIFF: {tif_path}")
        with Image.open(tif_path) as img:
            print(f"Original mode/size: {img.mode} {img.size}")
            # Convert to 8-bit grayscale for game use while preserving data for stats
            img_l = img.convert('L')
            img_resized = img_l.resize(target_size, Image.Resampling.NEAREST)
            img_resized.save(png_path, 'PNG', optimize=True)
        return True
    except Exception as e:
        print(f"Error converting with Pillow: {e}")
        return False


def compute_height_stats(tif_path: Path, target_size=(1536, 1024), colour_map_path: Path = None):
    """Return (min, sea_estimate, max) pixel values computed from TIFF.
    sea_estimate is determined by sampling pixels that match water in the
    existing color world map if available; otherwise it will try to find
    a value close to zero or return None.
    """
    if not PIL_AVAILABLE:
        raise RuntimeError("Pillow required to compute stats")

    with Image.open(tif_path) as img:
        # preserve original numeric data by converting to 'I' (32-bit integer)
        img_i = img.convert('I')

        width, height = img_i.size

        if NUMPY_AVAILABLE:
            arr = np.array(img_i, dtype=np.int32).reshape((height, width))
            minv = int(arr.min())
            maxv = int(arr.max())
        else:
            data = list(img_i.getdata())
            minv = int(min(data))
            maxv = int(max(data))

    sea_val = None
    if colour_map_path and colour_map_path.exists() and PIL_AVAILABLE:
        try:
            with Image.open(colour_map_path) as cmap:
                cmap = cmap.convert('RGB').resize((width, height), Image.Resampling.NEAREST)
                if NUMPY_AVAILABLE:
                    cmap_a = np.array(cmap)
                    r = cmap_a[:, :, 0].astype(np.int32)
                    g = cmap_a[:, :, 1].astype(np.int32)
                    b = cmap_a[:, :, 2].astype(np.int32)
                    water_mask = (b > 100) & (b > r + 10) & (b > g + 10)
                    if water_mask.sum() > 0:
                        sea_samples = arr[water_mask]
                        sea_val = int(np.median(sea_samples))
                else:
                    # Pure-Python water mask and sampling
                    cmap_pixels = list(cmap.getdata())
                    water_idxs = []
                    for i, (rc, gc, bc) in enumerate(cmap_pixels):
                        if bc > 100 and bc > rc + 10 and bc > gc + 10:
                            water_idxs.append(i)
                    if water_idxs:
                        # Need original tif data as flat list
                        with Image.open(tif_path) as timg:
                            tvals = list(timg.convert('I').getdata())
                        samples = [tvals[i] for i in water_idxs]
                        # median
                        samples.sort()
                        sea_val = int(samples[len(samples) // 2])
        except Exception:
            sea_val = None

    # Fallback heuristic for sea value when not found
    if sea_val is None:
        try:
            if NUMPY_AVAILABLE:
                flat = arr.flatten()
                # use histogram-like approach to pick a low-value peak
                hist, bins = np.histogram(flat, bins=256)
                peak_idx = int(hist.argmax())
                sea_candidate = int((bins[peak_idx] + bins[peak_idx + 1]) / 2)
            else:
                # pick most common value as candidate
                from collections import Counter

                with Image.open(tif_path) as timg:
                    tvals = list(timg.convert('I').getdata())
                counter = Counter(tvals)
                sea_candidate = int(counter.most_common(1)[0][0])

            if sea_candidate - minv <= (maxv - minv) * 0.25:
                sea_val = sea_candidate
        except Exception:
            sea_val = None

    return minv, sea_val, maxv


def verify_png_file(png_path: Path) -> bool:
    if not png_path.exists():
        return False
    if PIL_AVAILABLE:
        try:
            with Image.open(png_path) as img:
                print(f"Heightmap written: {png_path} ({img.mode} {img.size})")
                return True
        except Exception:
            return False
    return png_path.stat().st_size > 1000


def write_readme(readme_path: Path, stats: tuple):
    minv, sea, maxv = stats
    content = f"""# Gray Earth Heightmap

This document describes the Gray Earth heightmap produced for Airship Zero.

- Source: Natural Earth Gray Earth (public domain)
- Output: `assets/png/world-heightmap.png` (grayscale PNG)

Height statistics (pixel values from the source TIFF):

- Minimum (min pixel): {minv}
- Sea-level estimate (pixel): {sea if sea is not None else 'Not detected'}
- Maximum (max pixel): {maxv}

Notes:
- The Gray Earth TIFF encodes elevation as pixel values; the physical mapping
  (pixel -> meters) depends on dataset encoding. This script captures raw
  pixel min/sea/max so you can calibrate mapping to meters later.
- Recommended calibration steps:
  1. If you know the pixel value at sea level (from this file), call that 0 m.
  2. Sample a known high point (e.g., Mount Everest) and compute its pixel value
     from the TIFF to derive pixels-per-meter scaling.
  3. Alternatively use geographic DEM products (SRTM) if you need absolute meters.

How this README was generated:
The `map_gray_fetch.py` tool computes the statistics after downloading and
converting the TIFF and writes them here.
"""
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(content)


def main():
    print("=== Airship Zero Gray Earth Heightmap Fetch ===")
    project_root = Path(__file__).parent
    assets_dir = project_root / "assets" / "png"
    target_path = assets_dir / "world-heightmap.png"
    colour_map = assets_dir / "world-map.png"  # optional color map for sea sampling

    assets_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        zip_path = td_p / "gray_earth.zip"

        if not download_file(GRAY_EARTH_URL, zip_path):
            print("Download failed")
            sys.exit(1)

        extract_dir = td_p / "extracted"
        extract_dir.mkdir()
        if not extract_zip(zip_path, extract_dir):
            print("Extract failed")
            sys.exit(1)

        try:
            tif = find_tif_file(extract_dir)
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

        # Compute stats from original TIFF at native resolution
        try:
            stats = compute_height_stats(tif, colour_map_path=colour_map)
        except Exception as e:
            print(f"Could not compute stats: {e}")
            stats = (None, None, None)

        # Convert to game-ready PNG (resized grayscale)
        if not convert_tif_to_png_pillow(tif, target_path):
            print("Conversion failed")
            sys.exit(1)

        if not verify_png_file(target_path):
            print("Verification failed")
            sys.exit(1)

        # Write README with stats
        readme = Path(project_root) / "doc" / "MAP_GRAY_FETCH_README.md"
        write_readme(readme, stats)

        print("Done. Heightmap and README written.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Cancelled")
        sys.exit(1)
