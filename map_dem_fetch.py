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
import argparse
import math

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
    parser = argparse.ArgumentParser(description='Fetch ETOPO DEM and generate game heightmap PNG')
    parser.add_argument('--width', type=int, default=1536, help='target PNG width (pixels)')
    parser.add_argument('--height', type=int, default=1024, help='target PNG height (pixels)')
    parser.add_argument('--scale', type=float, default=1.0, help='scale multiplier to apply to default target size')
    parser.add_argument('--target-everest', type=float, default=None, help='If provided, compute a scale factor so measured max maps to this value (meters)')
    parser.add_argument('--cal-lat', type=float, default=None, help='Latitude to use for direct calibration (e.g. Everest)')
    parser.add_argument('--cal-lon', type=float, default=None, help='Longitude to use for direct calibration (e.g. Everest)')

    args = parser.parse_args()

    target_width = int(args.width * args.scale)
    target_height = int(args.height * args.scale)
    target_size = (target_width, target_height)

    print(f"=== Airship Zero DEM Fetch (ETOP0/2022) ===\nGenerating PNG at {target_size[0]}x{target_size[1]} (WxH)")
    project_root = Path(__file__).parent
    assets_dir = project_root / 'assets' / 'png'
    tiff_dir = project_root / 'assets' / 'tiff'
    assets_dir.mkdir(parents=True, exist_ok=True)
    tiff_dir.mkdir(parents=True, exist_ok=True)
    target_png = assets_dir / 'world-heightmap.png'

    # Persist TIFF in assets/tiff/ to avoid re-downloading
    persisted_tif = tiff_dir / 'ETOPO_2022_v1_30s_N90W180_surface.tif'
    if persisted_tif.exists():
        print(f'Found existing TIFF at {persisted_tif}, using it')
        tif_path = persisted_tif
    else:
        with tempfile.TemporaryDirectory() as td:
            td_p = Path(td)
            tmp_tif = td_p / 'etopo_surface.tif'

            if not download_file(ETOPO_URL, tmp_tif):
                print('Failed to download ETOPO GeoTIFF')
                sys.exit(1)

            # Move to assets/tiff for persistence
            shutil.move(str(tmp_tif), str(persisted_tif))
            tif_path = persisted_tif

    stats = compute_stats_and_write(tif_path, target_png, target_size)

    # After writing PNG, compute pixel range and write metadata JSON
    try:
        from PIL import Image
        import json
        with Image.open(target_png) as img:
            img_i = img.convert('I')
            pixels = list(img_i.getdata())
            pixel_min = int(min(pixels))
            pixel_max = int(max(pixels))

        minv, sea, maxv = stats
        offset = -minv
        # Compute optional calibration scale so measured max maps to a target Everest height
        scale = 1.0
        if args.target_everest is not None and maxv != 0:
            try:
                scale = float(args.target_everest) / float(maxv)
            except Exception:
                scale = 1.0

        # Optional direct calibration: sample a given lat/lon and compute scale so that
        # sampled elevation at that point matches target-everest exactly. This is often
        # preferable to using global max because downsampling may move the global max.
        if args.cal_lat is not None and args.cal_lon is not None and args.target_everest is not None:
            try:
                from PIL import Image
                import numpy as np

                with Image.open(target_png) as img:
                    img_i = img.convert('I')
                    w, h = img_i.size
                    arr = np.array(img_i, dtype=np.uint16).reshape((h, w))

                # convert lat/lon to pixel coords
                def deg_to_pixel(lat, lon, width, height):
                    lon = ((lon + 180.0) % 360.0) - 180.0
                    x = (lon + 180.0) / 360.0 * (width - 1)
                    y = (90.0 - lat) / 180.0 * (height - 1)
                    return x, y

                def bilinear_sample(arr, x, y):
                    x0 = int(math.floor(x))
                    y0 = int(math.floor(y))
                    x1 = min(x0 + 1, arr.shape[1] - 1)
                    y1 = min(y0 + 1, arr.shape[0] - 1)
                    wx = x - x0
                    wy = y - y0
                    v00 = float(arr[y0, x0])
                    v10 = float(arr[y0, x1])
                    v01 = float(arr[y1, x0])
                    v11 = float(arr[y1, x1])
                    a = v00 * (1 - wx) + v10 * wx
                    b = v01 * (1 - wx) + v11 * wx
                    return a * (1 - wy) + b * wy

                x, y = deg_to_pixel(args.cal_lat, args.cal_lon, w, h)
                sampled = bilinear_sample(arr, x, y)
                sampled_m = float(sampled) - float(offset)
                if sampled_m != 0:
                    scale = float(args.target_everest) / sampled_m
                    print(f'Calibration: sampled at {args.cal_lat},{args.cal_lon} -> {sampled_m:.2f} m, scale -> {scale:.6f}')
            except Exception as e:
                print('Warning: calibration by point failed:', e)

        # Write metadata that includes TIFF-derived authoritative min/max
        # and the PNG pixel range so runtime code can perform a linear map
        # from pixel -> metres using the TIFF extrema.
        meta = {
            'min_elev': minv,
            'sea': sea,
            'max_elev': maxv,
            'offset': offset,
            'scale': scale,
            'tiff_min': minv,
            'tiff_max': maxv,
            'pixel_min': pixel_min,
            'pixel_max': pixel_max
        }
        meta_path = assets_dir / 'world-heightmap.meta.json'
        meta_path.write_text(json.dumps(meta, indent=2))
        print('Wrote metadata:', meta_path)
    except Exception as e:
        print('Warning: could not write metadata JSON:', e)

    # Update README as well
    readme = project_root / 'doc' / 'MAP_DEM_FETCH_README.md'
    write_readme(readme, stats)
    print('Wrote', target_png)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Cancelled')
        sys.exit(1)
