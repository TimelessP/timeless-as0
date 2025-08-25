# ETOPO DEM Heightmap

This file documents the ETOPO DEM used to generate the global heightmap for
Airship Zero.

Source: NOAA ETOPO 2022 (public domain)

Generated file: `assets/png/world-heightmap.png` (16-bit PNG with zero-based offset)

Measured statistics (meters):
- Minimum: -9674
- Sea level (0 m) detected: 0
- Maximum: 5968

To map pixel -> meters for the saved PNG: the script offset the elevation by
9674 so that the minimum elevation maps to 0. To convert a pixel value V in
the PNG back to meters: meters = int(V) - 9674
