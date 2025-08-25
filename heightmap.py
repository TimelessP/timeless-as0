"""
HeightMap helper for Airship Zero

Provides HeightMap class which loads a 16-bit PNG heightmap once and
exposes a `height_at(lat, lon, precision=4)` method that returns elevation in
metres. By default the method uses bilinear interpolation; when `precision`
is provided (number of decimal places for lat/lon) the method will perform a
small area average to reduce aliasing for very fine coordinates (default 4).

Usage:
    from heightmap import HeightMap
    hm = HeightMap()  # loads assets/png/world-heightmap.png and json calibration data
    z = hm.height_at(40.7128, -74.0060)

Requires Pillow; NumPy optional (faster array handling).
"""
from pathlib import Path
import math
import warnings

try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except Exception:
    np = None
    NUMPY_AVAILABLE = False


class HeightMap:
    def __init__(self, image_path: str = None, calibration_path: str = None):
        project_root = Path(__file__).parent
        self.image_path = Path(image_path) if image_path else project_root / 'assets' / 'png' / 'world-heightmap.png'
        self.meta_path = Path(calibration_path) if calibration_path else project_root / 'assets' / 'png' / 'world-heightmap.meta.json'

        if not PIL_AVAILABLE:
            raise RuntimeError('Pillow is required to load heightmap')

        if not self.image_path.exists():
            raise FileNotFoundError(f'Heightmap image not found: {self.image_path}')

        # Calibration: read metadata JSON if present (preferred)
        self._offset = 0
        self._scale = 1.0
        # TIFF-derived authoritative extrema (if present)
        self._tiff_min = None
        self._tiff_max = None
        self._pixel_min = None
        self._pixel_max = None
        try:
            import json
            if self.meta_path.exists():
                meta = json.loads(self.meta_path.read_text())
                if 'offset' in meta:
                    self._offset = int(meta['offset'])
                elif 'min_elev' in meta:
                    self._offset = -int(meta['min_elev'])

                if 'scale' in meta:
                    try:
                        self._scale = float(meta['scale'])
                    except Exception:
                        self._scale = 1.0

                # tiff_min/tiff_max + pixel_min/pixel_max provide an authoritative
                # linear mapping from stored pixel -> metres. Prefer this when available.
                if 'tiff_min' in meta and 'tiff_max' in meta and 'pixel_min' in meta and 'pixel_max' in meta:
                    try:
                        self._tiff_min = float(meta['tiff_min'])
                        self._tiff_max = float(meta['tiff_max'])
                        self._pixel_min = int(meta['pixel_min'])
                        self._pixel_max = int(meta['pixel_max'])
                    except Exception:
                        self._tiff_min = None
                        self._tiff_max = None
                        self._pixel_min = None
                        self._pixel_max = None
        except Exception:
            # fallback to defaults
            self._offset = 0
            self._scale = 1.0

        # Load image data once
        img = Image.open(self.image_path)
        # Convert to 16-bit unsigned array representation
        try:
            img = img.convert('I')
        except Exception:
            img = img.copy().convert('I')

        self.width, self.height = img.size

        if NUMPY_AVAILABLE:
            arr = np.array(img, dtype=np.uint16).reshape((self.height, self.width))
            # store as float array for interpolation speed
            self._arr = arr.astype(np.float64)
        else:
            # fallback: store as a list-of-lists
            data = list(img.getdata())
            rows = [data[i * self.width:(i + 1) * self.width] for i in range(self.height)]
            self._arr = rows

    def _sample_bilinear(self, x: float, y: float) -> float:
        """Bilinear sample on internal array at float pixel coords x,y (0..w-1, 0..h-1)."""
        if x < 0:
            x = 0.0
        if y < 0:
            y = 0.0
        if x > self.width - 1:
            x = self.width - 1.0
        if y > self.height - 1:
            y = self.height - 1.0

        x0 = int(math.floor(x))
        y0 = int(math.floor(y))
        x1 = min(x0 + 1, self.width - 1)
        y1 = min(y0 + 1, self.height - 1)

        wx = x - x0
        wy = y - y0

        if NUMPY_AVAILABLE:
            v00 = float(self._arr[y0, x0])
            v10 = float(self._arr[y0, x1])
            v01 = float(self._arr[y1, x0])
            v11 = float(self._arr[y1, x1])
        else:
            v00 = float(self._arr[y0][x0])
            v10 = float(self._arr[y0][x1])
            v01 = float(self._arr[y1][x0])
            v11 = float(self._arr[y1][x1])

        a = v00 * (1 - wx) + v10 * wx
        b = v01 * (1 - wx) + v11 * wx
        return a * (1 - wy) + b * wy

    def _deg_to_pixel(self, lat: float, lon: float):
        """Convert geographic coordinates to pixel coordinates (x,y)."""
        # Wrap longitude
        lon = ((lon + 180.0) % 360.0) - 180.0
        # X: lon -180..180 maps to 0..width-1
        x = (lon + 180.0) / 360.0 * (self.width - 1)
        # Y: lat 90..-90 maps to 0..height-1
        y = (90.0 - lat) / 180.0 * (self.height - 1)
        return x, y

    def height_at(self, lat: float, lon: float, precision: int = 4) -> float:
        """Return height in metres at given lat, lon.

        precision: decimal places for lat/lon (default 4). For precision >=4 the
        method performs a small area average (3x3) across +/- 0.5 * 10^-precision deg
        to reduce aliasing. Returns a float in metres (may be negative).
        """
        if not (-90.0 <= lat <= 90.0):
            raise ValueError('lat out of range')

        x, y = self._deg_to_pixel(lat, lon)

        # If precision requires averaging, compute sample grid
        if precision and precision >= 4:
            # area half-size in degrees
            ddeg = 0.5 * (10 ** (-precision))
            # Convert small degree delta to pixel deltas
            dx = ddeg / 360.0 * (self.width - 1)
            dy = ddeg / 180.0 * (self.height - 1)
            # sample 3x3 grid
            samples = []
            for sx in (-1, 0, 1):
                for sy in (-1, 0, 1):
                    sxpos = x + sx * dx
                    sypos = y + sy * dy
                    samples.append(self._sample_bilinear(sxpos, sypos))
            val = sum(samples) / len(samples)
        else:
            val = self._sample_bilinear(x, y)

        # Convert stored pixel value back to metres.
        # Prefer TIFF-derived linear mapping if available:
        if self._tiff_min is not None and self._tiff_max is not None and self._pixel_min is not None and self._pixel_max is not None:
            # linear interpolation from pixel range to tiff elevation range
            p = float(val)
            # Clamp to pixel range to avoid wild extrapolation
            p = max(float(self._pixel_min), min(float(self._pixel_max), p))
            metres = self._tiff_min + (p - float(self._pixel_min)) * (self._tiff_max - self._tiff_min) / max(1.0, float(self._pixel_max - self._pixel_min))
            return float(metres)

        # Fallback: use offset + scale (legacy behavior)
        metres = (float(val) - float(self._offset)) * float(self._scale)
        return metres


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Test HeightMap lookup')
    parser.add_argument('lat', type=float, help='Latitude', default=27.9881)
    parser.add_argument('lon', type=float, help='Longitude', default=86.925)
    parser.add_argument('--precision', type=int, default=4, help='Decimal places for averaging')
    args = parser.parse_args()

    hm = HeightMap()
    z = hm.height_at(args.lat, args.lon, precision=args.precision)
    print(f'Height at {args.lat:.6f},{args.lon:.6f} = {z:.2f} m')
