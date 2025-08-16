# Map Fetch Tool

## Overview

`map_fetch.py` is a development tool for updating the world map used in Airship Zero. It downloads high-quality topographical world map data from Natural Earth and converts it to the PNG format required by the game.

## Features

- Downloads Natural Earth 2 world map data (public domain)
- Converts TIF raster data to PNG format
- Automatically resizes to game requirements (1536x1024)
- Creates backup of existing map
- Verifies successful conversion

## Usage

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the map fetch tool
python map_fetch.py

# Or make it executable and run directly
chmod +x map_fetch.py
./map_fetch.py
```

## Natural Earth 2 Features

- **Idealized world environment** with minimal human influence
- **Perfect retro aesthetic** for the steampunk airship setting
- **High-quality topographical relief** with natural coloring
- **Public domain license** - no attribution required
- **Professional cartographic quality** from renowned map creators

## Technical Details

- **Source**: Natural Earth (naturalearthdata.com)
- **Dataset**: Natural Earth 2 - Shaded Relief with Water
- **Resolution**: Medium (16,200 x 8,100 source, resized to 1536 x 1024)
- **Format**: PNG with RGB color
- **License**: Public Domain
- **Size**: ~2.1MB (optimized)

## Dependencies

The tool requires Pillow for image processing:

```bash
pip install Pillow
```

## Prime Meridian Centering

The Natural Earth maps are properly projected with longitude 0° (Greenwich/Prime Meridian) at the horizontal center of the image, making them perfect for navigation systems that expect this standard cartographic convention.

## Coordinate System Compatibility

The new map maintains full compatibility with the existing Airship Zero coordinate conversion system. All waypoint placement, navigation calculations, and route following functions work seamlessly with the updated map data.
