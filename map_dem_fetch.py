#!/usr/bin/env python3
"""
ETOPO DEM Fetcher for Airship Zero

Downloads ETOPO 2022 (30 arc-second global GeoTIFF), converts it to a
game-ready 16-bit PNG heightmap at `assets/png/world-heightmap.png`, and
writes min/sea/max (meters) to the README.

Note: This script attempts to use Pillow + NumPy for processing. If NumPy is
missing, the script will attempt a slower pure-Pillow path where possible.
"""
from pathlib import Path
import os
import sys
import urllib.request
import urllib.error
import shutil
import tempfile

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

# ETOPO2022 30s global surface GeoTIFF (N90W180 layout)
ETOPO_URL = (
    "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/30s/"
    "30s_surface_elev_gtif/ETOPO_2022_v1_30s_N90W180_surface.tif"
)


def download_file(url: str, dest: Path) -> bool:
    try:
        print(f"Downloading {url}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; AirshipZero/1.0)"})
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, 'wb') as out:
            shutil.copyfileobj(r, out)
        return True
    except urllib.error.HTTPError as e:
        print(f"HTTP error: {e}")
        return False
    except Exception as e:
        print(f"Download error: {e}")
        return False


def compute_stats_and_write(tif_path: Path, png_path: Path, target_size=(1536, 1024)):
    if not PIL_AVAILABLE:
        raise RuntimeError("Pillow is required")

    print(f"Opening TIFF: {tif_path}")
    # Allow opening large GeoTIFFs (we will downsample before materializing arrays)
    Image.MAX_IMAGE_PIXELS = None
    with Image.open(tif_path) as src:
        width, height = src.size
        # Determine integer reduction factor to get near target_size
        tx, ty = target_size
        import math
        factor = max(1, math.ceil(max(width / tx, height / ty)))
        if factor > 1:
            print(f"Downsampling by factor {factor} to avoid large memory usage")
            src_small = src.reduce(factor)
        else:
            src_small = src

        # Convert to 32-bit integer representation on the smaller image
        src_i = src_small.convert('I')
        sw, sh = src_i.size

        if NUMPY_AVAILABLE:
            arr = np.array(src_i, dtype=np.int32).reshape((sh, sw))
            minv = int(arr.min())
            maxv = int(arr.max())
        else:
            data = list(src_i.getdata())
            minv = int(min(data))
            maxv = int(max(data))

    # Sea level is zero meters in ETOPO; try to detect presence of 0 in data
    sea_val = 0 if (minv <= 0 <= maxv) else None

    print(f"Stats (meters): min={minv}, sea={sea_val}, max={maxv}")

    # Create unsigned 16-bit image by offsetting so minimum becomes 0
    offset = -minv

    if NUMPY_AVAILABLE:
        # Reconstruct a resized 16-bit PNG from the downsampled array
        u16 = (arr + offset).clip(0, 65535).astype(np.uint16)
        img_u16 = Image.fromarray(u16, mode='I;16')
        img_resized = img_u16.resize(target_size, resample=Image.Resampling.NEAREST)
        img_resized.save(png_path, format='PNG')
    else:
        # Pure PIL fallback: map pixels to 0..65535 manually
        with Image.open(tif_path) as src:
            src_i = src.convert('I')
            # Resize first (may lose precision) then remap
            resized = src_i.resize(target_size, resample=Image.Resampling.NEAREST)
            # Map pixels
            pixels = list(resized.getdata())
            mapped = [max(0, min(65535, p + offset)) for p in pixels]
            out = Image.new('I', resized.size)
            out.putdata(mapped)
            out.save(png_path, format='PNG')

    return minv, sea_val, maxv


def write_readme(readme_path: Path, stats: tuple):
    minv, sea, maxv = stats
    offset = -minv
    content = f"""# ETOPO DEM Heightmap

This file documents the ETOPO DEM used to generate the global heightmap for
Airship Zero.

Source: NOAA ETOPO 2022 (public domain)

Generated file: `assets/png/world-heightmap.png` (16-bit PNG with zero-based offset)

Measured statistics (meters):
- Minimum: {minv}
- Sea level (0 m) detected: {sea}
- Maximum: {maxv}

To map pixel -> meters for the saved PNG: the script offset the elevation by
{offset} so that the minimum elevation maps to 0. To convert a pixel value V in
the PNG back to meters: meters = int(V) - {offset}
"""
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(content)


def main():
    print("=== Airship Zero DEM Fetch (ETOP0/2022) ===")
    project_root = Path(__file__).parent
    assets_dir = project_root / 'assets' / 'png'
    assets_dir.mkdir(parents=True, exist_ok=True)
    target_png = assets_dir / 'world-heightmap.png'

    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        tif_path = td_p / 'etopo_surface.tif'

        if not download_file(ETOPO_URL, tif_path):
            print('Failed to download ETOPO GeoTIFF')
            sys.exit(1)

        stats = compute_stats_and_write(tif_path, target_png)
        readme = project_root / 'doc' / 'MAP_DEM_FETCH_README.md'
        write_readme(readme, stats)

        print('Wrote', target_png)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Cancelled')
        sys.exit(1)
