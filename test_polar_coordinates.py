#!/usr/bin/env python3
"""Test script to validate polar coordinate handling"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core_simulator import get_simulator
from terrain_mesh import TerrainMesh
from heightmap import HeightMap

def test_polar_coordinates():
    """Test mesh generation at various polar coordinates"""
    print("Testing polar coordinate handling...")
    
    # Initialize components
    simulator = get_simulator()
    heightmap = HeightMap()
    
    # Load world map (we need this for TerrainMesh)
    import pygame
    from main import get_assets_dir
    
    pygame.init()
    assets_dir = get_assets_dir()
    world_map_path = os.path.join(assets_dir, "png", "world-map.png")
    world_map = pygame.image.load(world_map_path)
    
    terrain_mesh = TerrainMesh(heightmap, world_map)
    
    # Test coordinates near poles
    test_positions = [
        (89.5, 0.0, 1000.0),    # Very close to North Pole
        (89.0, 45.0, 1000.0),   # Near North Pole, different longitude
        (-89.5, 180.0, 1000.0), # Very close to South Pole
        (-89.0, -90.0, 1000.0), # Near South Pole, different longitude
        (85.0, 0.0, 1000.0),    # High latitude but not extreme
        (-85.0, 0.0, 1000.0),   # High south latitude
    ]
    
    for lat, lon, alt in test_positions:
        print(f"\nTesting position: lat={lat}, lon={lon}, alt={alt}")
        try:
            # Set simulator position directly in state
            state = simulator.get_state()
            state["navigation"]["position"]["latitude"] = lat
            state["navigation"]["position"]["longitude"] = lon
            state["navigation"]["position"]["altitude"] = alt
            
            # Try to generate mesh
            terrain_mesh.generate_dual_lod_mesh_around_position(lat, lon, alt)
            print(f"  ✓ Mesh generation successful at ({lat}, {lon})")
            
            # Get stats
            inner_count = len(terrain_mesh.inner_land_triangles) + len(terrain_mesh.inner_sea_triangles)
            outer_count = len(terrain_mesh.outer_land_triangles) + len(terrain_mesh.outer_sea_triangles)
            print(f"  Inner triangles: {inner_count}, Outer triangles: {outer_count}")
            
        except Exception as e:
            import traceback
            print(f"  ✗ Error at ({lat}, {lon}): {e}")
            print(f"    Full traceback:")
            traceback.print_exc()
            return False
    
    print("\n✓ All polar coordinate tests passed!")
    return True

if __name__ == "__main__":
    success = test_polar_coordinates()
    sys.exit(0 if success else 1)
