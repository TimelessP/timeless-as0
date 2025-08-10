#!/usr/bin/env python3
"""
Map Fetch Tool for Airship Zero

Downloads Natural Earth 2 world map data and converts it to PNG format
for use in the airship navigation system. This is a development tool only.

Natural Earth 2: Idealized world environment with little human influence,
perfect for the retro airship aesthetic.

License: Natural Earth data is public domain, no attribution required.
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path
import tempfile

# Optional dependencies for advanced processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Natural Earth 2 download URLs
NATURAL_EARTH_BASE_URL = "https://naciscdn.org/naturalearth"
NE2_URLS = {
    "high_res": f"{NATURAL_EARTH_BASE_URL}/10m/raster/NE2_HR_LC_SR_W.zip",
    "medium_res": f"{NATURAL_EARTH_BASE_URL}/10m/raster/NE2_LR_LC_SR_W.zip"
}

def download_file(url: str, dest_path: Path) -> bool:
    """Download a file from URL to destination path."""
    try:
        print(f"Downloading {url}...")
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            
            with open(dest_path, 'wb') as f:
                downloaded = 0
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}%", end='', flush=True)
                
                print()  # New line after progress
                
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def extract_zip(zip_path: Path, extract_dir: Path) -> bool:
    """Extract ZIP file to directory."""
    try:
        print(f"Extracting {zip_path.name}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        return True
    except Exception as e:
        print(f"Error extracting {zip_path}: {e}")
        return False

def find_tif_file(directory: Path) -> Path:
    """Find the main .tif file in the extracted directory."""
    tif_files = list(directory.glob("*.tif"))
    if not tif_files:
        raise FileNotFoundError("No .tif files found in extracted directory")
    
    # Look for the main file (usually the largest or with specific naming)
    main_file = None
    for tif_file in tif_files:
        if "SR_W" in tif_file.name:  # Shaded Relief with Water
            main_file = tif_file
            break
    
    if not main_file:
        main_file = max(tif_files, key=lambda f: f.stat().st_size)
    
    print(f"Found main TIF file: {main_file.name}")
    return main_file

def convert_tif_to_png_pillow(tif_path: Path, png_path: Path, target_size: tuple = (1536, 1024)) -> bool:
    """Convert TIF to PNG using Pillow with resizing."""
    try:
        print(f"Converting {tif_path.name} to PNG using Pillow...")
        
        with Image.open(tif_path) as img:
            print(f"Original image size: {img.size}")
            print(f"Original image mode: {img.mode}")
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to target dimensions
            img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Save as PNG
            img_resized.save(png_path, 'PNG', optimize=True)
            print(f"Saved resized PNG: {png_path} ({target_size[0]}x{target_size[1]})")
            
        return True
    except Exception as e:
        print(f"Error converting with Pillow: {e}")
        return False

def convert_tif_to_png_system(tif_path: Path, png_path: Path, target_size: tuple = (1536, 1024)) -> bool:
    """Convert TIF to PNG using system ImageMagick."""
    try:
        print(f"Converting {tif_path.name} to PNG using ImageMagick...")
        
        # Try ImageMagick convert command
        cmd = f"convert '{tif_path}' -resize {target_size[0]}x{target_size[1]}! '{png_path}'"
        result = os.system(cmd)
        
        if result == 0 and png_path.exists():
            print(f"Successfully converted using ImageMagick")
            return True
        else:
            print(f"ImageMagick conversion failed (exit code: {result})")
            return False
            
    except Exception as e:
        print(f"Error with ImageMagick conversion: {e}")
        return False

def verify_png_file(png_path: Path) -> bool:
    """Verify the PNG file is valid and has correct dimensions."""
    try:
        if PIL_AVAILABLE:
            with Image.open(png_path) as img:
                print(f"Final PNG size: {img.size}")
                print(f"Final PNG mode: {img.mode}")
                return True
        else:
            # Basic file existence check
            if png_path.exists() and png_path.stat().st_size > 1000:
                print(f"PNG file exists: {png_path} ({png_path.stat().st_size} bytes)")
                return True
            else:
                print(f"PNG file verification failed")
                return False
    except Exception as e:
        print(f"Error verifying PNG: {e}")
        return False

def main():
    """Main execution function."""
    print("=== Airship Zero Map Fetch Tool ===")
    print("Downloading Natural Earth 2 world map data...\n")
    
    # Get project root directory
    project_root = Path(__file__).parent
    assets_dir = project_root / "assets" / "png"
    target_map_path = assets_dir / "world-map.png"
    
    # Create assets directory if it doesn't exist
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Check current map
    if target_map_path.exists():
        print(f"Current map found: {target_map_path}")
        current_size = target_map_path.stat().st_size
        print(f"Current size: {current_size} bytes")
        
        # Backup current map
        backup_path = target_map_path.with_suffix('.png.backup')
        shutil.copy2(target_map_path, backup_path)
        print(f"Backed up current map to: {backup_path}")
    
    # Create temporary directory for downloads
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"Using temporary directory: {temp_path}")
        
        # Determine which resolution to download
        resolution = "medium_res"  # Start with medium for faster download
        
        # Check available processing capabilities
        print(f"\nProcessing capabilities:")
        print(f"  PIL (Pillow): {'Available' if PIL_AVAILABLE else 'Not available'}")
        print(f"  NumPy: {'Available' if NUMPY_AVAILABLE else 'Not available'}")
        
        if not PIL_AVAILABLE:
            print("\nNote: PIL not available. Will try system ImageMagick.")
        
        # Download the map data
        zip_filename = f"natural_earth_2_{resolution}.zip"
        zip_path = temp_path / zip_filename
        
        if not download_file(NE2_URLS[resolution], zip_path):
            print("Failed to download map data")
            return 1
        
        # Extract the ZIP file
        extract_dir = temp_path / "extracted"
        extract_dir.mkdir()
        
        if not extract_zip(zip_path, extract_dir):
            print("Failed to extract map data")
            return 1
        
        # Find the main TIF file
        try:
            tif_path = find_tif_file(extract_dir)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return 1
        
        # Convert TIF to PNG
        temp_png_path = temp_path / "world-map.png"
        target_size = (1536, 1024)  # Match current map dimensions
        
        conversion_success = False
        
        # Try Pillow first if available
        if PIL_AVAILABLE:
            conversion_success = convert_tif_to_png_pillow(tif_path, temp_png_path, target_size)
        
        # Fallback to ImageMagick if Pillow failed or not available
        if not conversion_success:
            conversion_success = convert_tif_to_png_system(tif_path, temp_png_path, target_size)
        
        if not conversion_success:
            print("Failed to convert TIF to PNG")
            print("Please install either:")
            print("  pip install Pillow")
            print("  or system ImageMagick: sudo apt-get install imagemagick")
            return 1
        
        # Verify the converted PNG
        if not verify_png_file(temp_png_path):
            print("PNG verification failed")
            return 1
        
        # Copy the new map to assets directory
        shutil.copy2(temp_png_path, target_map_path)
        print(f"\nSuccessfully installed new world map: {target_map_path}")
        
        # Final verification
        if verify_png_file(target_map_path):
            new_size = target_map_path.stat().st_size
            print(f"New map size: {new_size} bytes")
            
            if target_map_path.with_suffix('.png.backup').exists():
                size_diff = new_size - target_map_path.with_suffix('.png.backup').stat().st_size
                print(f"Size change: {size_diff:+d} bytes")
            
            print("\n=== Map fetch completed successfully! ===")
            print("The new Natural Earth 2 map is ready for use.")
            print("Features:")
            print("  - Idealized world environment")
            print("  - Perfect for retro airship aesthetic")
            print("  - High quality topographical relief")
            print("  - Public domain license")
            
            return 0
        else:
            print("Final verification failed")
            return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nDownload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
