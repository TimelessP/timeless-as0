# Gray Earth Heightmap

This document describes the Gray Earth heightmap produced for Airship Zero.

- Source: Natural Earth Gray Earth (public domain)
- Output: `assets/png/world-heightmap.png` (grayscale PNG)

Height statistics (pixel values from the source TIFF):

- Minimum (min pixel): 64
- Sea-level estimate (pixel): 146
- Maximum (max pixel): 252

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
