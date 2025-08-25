# ETOPO DEM Heightmap

This file documents the ETOPO DEM used to generate the global heightmap for
Airship Zero.

Source: NOAA ETOPO 2022 (public domain)

Generated file: `assets/png/world-heightmap.png` (16-bit PNG with zero-based offset)

Measured statistics (meters) (from the most recent generation):
- Minimum: -10297
- Sea level (0 m) detected: 0
- Maximum (measured on downsampled PNG): 6306

Calibration & TIFF-based linear mapping
--------------------------------------
This pipeline now trusts the extrema derived from the source GeoTIFF as the
canonical calibration points. The metadata JSON written alongside the PNG
contains both the TIFF-measured minimum/maximum elevations (metres) and the
pixel range in the saved 16-bit PNG. Example `assets/png/world-heightmap.meta.json`:

```json
{
	"min_elev": -10297,
	"sea": 0,
	"max_elev": 6306,
	"offset": 10297,
	"scale": 1.4724199760749486,
	"pixel_min": 0,
	"pixel_max": 16603
}
```

Runtime mapping
---------------
When `heightmap.py` converts a stored pixel value P back to metres it now
prefers a linear mapping derived from the TIFF extrema and the PNG pixel range.
The preferred formula is:

		metres = tiff_min + (P - pixel_min) * (tiff_max - tiff_min) / (pixel_max - pixel_min)

Where:
- `tiff_min` / `tiff_max` are `min_elev` / `max_elev` recorded from the TIFF
- `pixel_min` / `pixel_max` are the min/max pixel values found in the saved PNG

This gives a clear, auditable mapping from stored pixels to metres that is
anchored to the source DEM extrema. If for any reason the metadata lacks the
TIFF extrema the runtime falls back to the previous `offset`+`scale` method.

Centering and coordinate convention
----------------------------------
- The generated PNG uses a global 360°×180° coverage where the image centre
	corresponds to latitude=0°, longitude=0°. Longitudes are wrapped so -180..+180
	maps to x=0..width-1; latitudes 90..-90 map to y=0..height-1.

Commands & parameters used
--------------------------
Examples used during development (run from project root):

Generate a doubled-resolution PNG (3072x2048) using the persisted TIFF:

```bash
python map_dem_fetch.py --scale 2.0
```

```bash
python - <<'PY'
from heightmap import HeightMap
hm = HeightMap()
tests = [
    ("Mount Everest", 27.9881, 86.9250, 8848.86),
    ("Mount Kilimanjaro", 3.0674, 37.3556, 5895),
    ("Mauna Kea", 19.8206, -155.4681, 4207),
    ("Dead Sea (shore)", 31.5590, 35.4732, -430),
    ("New York City (Manhattan)", 40.7128, -74.0060, 10),
    ("London (central)", 51.5074, -0.1278, 11),
    ("Challenger Deep", 11.368, 142.199, -10994),
]
print("name\tlat\tlon\texpected_m\treturned_m")
for name, lat, lon, expected in tests:
    try:
        z = hm.height_at(lat, lon, precision=4)
    except Exception as e:
        z = f"ERROR: {e}"
    print(f"{name}\t{lat}\t{lon}\t{expected}\t{z}")
PY
```

Regenerate and write metadata; because we now use TIFF extrema they are read
from the processed image and written to `assets/png/world-heightmap.meta.json`.

Notes on accuracy
-----------------
- We trust TIFF-measured min/max for calibration, but the saved PNG is a
	downsampled representation; downsampling blurs local features and may change
	the location of the numeric max/min slightly. The linear mapping keeps the
	global scale faithful to the source DEM but local absolute errors can remain.
- For exact per-point accuracy use an on-demand reader of the original TIFF
	(e.g., `rasterio`) which returns native-resolution values rather than a
	down-sampled proxy. The TIFF is persisted at `assets/tiff/` so this can be
	added later without re-downloading.

Files produced/updated
----------------------
- `assets/png/world-heightmap.png` — 16-bit PNG heightmap (generated)
- `assets/png/world-heightmap.meta.json` — machine-readable calibration metadata
- `assets/tiff/ETOPO_2022_v1_30s_N90W180_surface.tif` — persisted source GeoTIFF (kept out of git via `.gitignore`)

If you want me to implement a rasterio-based on-demand sampler or to
regenerate the PNG at a higher resolution to reduce local downsampling
errors, tell me which and I'll implement it.
