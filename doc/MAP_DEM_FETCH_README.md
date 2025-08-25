# ETOPO DEM Heightmap

This file documents the ETOPO DEM used to generate the global heightmap for
Airship Zero.

Source: NOAA ETOPO 2022 (public domain)

Generated file: `assets/png/world-heightmap.png` (16-bit PNG with zero-based offset)

Measured statistics (meters) (from the most recent generation):
- Minimum: -10297
- Sea level (0 m) detected: 0
- Maximum (measured on downsampled PNG): 6306

Calibration & scaling
---------------------
The raw downsampled PNG stores elevation as unsigned 16-bit pixels where the
minimum measured elevation was offset to 0. The following metadata file was
written alongside the PNG and contains the calibration values used by the
game at runtime:

`assets/png/world-heightmap.meta.json` (sample contents):

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

This means the stored pixel value P maps to metres via:

		metres = (P - offset) * scale

Where `offset` = 10297 and `scale` = 1.472419976... (computed during the
last regeneration to make the sampled elevation at Mount Everest equal to
8848.86 m — see commands below).

Commands & parameters used
--------------------------
The DEM pipeline and calibration were run locally with the following commands
during development (examples shown run from the project root):

1) Regenerate the heightmap PNG at double the default resolution (3072x2048)
	 and compute an initial scale based on the global maximum:

```bash
python map_dem_fetch.py --scale 2.0
```

2) Regenerate and perform direct-point calibration so the sampled value at
	 Mount Everest (lat=27.9881, lon=86.9250) maps exactly to 8848.86 m:

```bash
python map_dem_fetch.py --scale 2.0 --target-everest 8848.86 --cal-lat 27.9881 --cal-lon 86.9250
```

Notes on calibration and accuracy
--------------------------------
- The ETOPO GeoTIFF is very large; the script down-samples before converting to
	avoid memory / decompression issues. Down-sampling reduces local detail and
	shifts the measured min/max values compared to the original DEM.
- To compensate, we write a `scale` into the metadata which is applied at
	runtime by `heightmap.py`. For the development run above the `scale` was
	computed by sampling the generated PNG at the Everest coordinates and
	computing `scale = target_everest / sampled_value_meters`.
- This is a practical compromise for a global, low-memory heightmap used by
	the game. For exact geodetic heights at arbitrary lat/lon, use the original
	GeoTIFF with a raster library (e.g., `rasterio`) to read values on-demand.

Files produced/updated
----------------------
- `assets/png/world-heightmap.png` — 16-bit PNG heightmap (generated)
- `assets/png/world-heightmap.meta.json` — machine-readable calibration metadata
- `assets/tiff/ETOPO_2022_v1_30s_N90W180_surface.tif` — persisted source GeoTIFF (kept out of git via `.gitignore`)

If you want me to regenerate the PNG at a different resolution or implement
an on-demand raster reader using `rasterio` for higher-precision sampling,
tell me which you'd prefer and I'll prepare it.
