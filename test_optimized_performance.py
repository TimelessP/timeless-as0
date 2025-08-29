#!/usr/bin/env python3
"""Test script to validate performance improvements"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

import pygame
from core_simulator import get_simulator
from terrain_mesh import TerrainMesh
from heightmap import HeightMap
from main import get_assets_dir

def test_optimized_performance():
    """Test mesh generation performance with optimizations"""
    print("Testing optimized mesh performance...")
    
    # Initialize components
    pygame.init()
    assets_dir = get_assets_dir()
    world_map_path = os.path.join(assets_dir, "png", "world-map.png")
    world_map = pygame.image.load(world_map_path)
    
    simulator = get_simulator()
    heightmap = HeightMap()
    terrain_mesh = TerrainMesh(heightmap, world_map)
    
    # Test a few positions
    test_positions = [
        (40.0, -74.0, 1000.0),      # NYC
        (51.5, 0.0, 1000.0),        # London
        (-33.9, 151.2, 1000.0),     # Sydney
    ]
    
    print(f"Current mesh settings:")
    print(f"  Inner resolution: {terrain_mesh.inner_mesh_resolution}x{terrain_mesh.inner_mesh_resolution}")
    print(f"  Outer resolution: {terrain_mesh.outer_mesh_resolution}x{terrain_mesh.outer_mesh_resolution}")
    print(f"  Inner radius: {terrain_mesh.inner_radius_deg}° (~{terrain_mesh.inner_radius_deg * 111:.0f}km)")
    print(f"  Outer radius: {terrain_mesh.outer_radius_deg}° (~{terrain_mesh.outer_radius_deg * 111:.0f}km)")
    print(f"  Horizontal scale: {terrain_mesh.scale_horizontal}")
    print(f"  Vertical scale: {terrain_mesh.scale_vertical}")
    
    generation_times = []
    
    for i, (lat, lon, alt) in enumerate(test_positions):
        print(f"\nTest {i+1}: {lat}, {lon}")
        
        # Set simulator position
        state = simulator.get_state()
        state["navigation"]["position"]["latitude"] = lat
        state["navigation"]["position"]["longitude"] = lon
        state["navigation"]["position"]["altitude"] = alt
        
        # Time the mesh generation
        start_time = time.time()
        terrain_mesh.generate_dual_lod_mesh_around_position(lat, lon, alt)
        end_time = time.time()
        
        generation_time = (end_time - start_time) * 1000  # Convert to ms
        generation_times.append(generation_time)
        
        print(f"  Generation time: {generation_time:.2f} ms")
        
        # Get triangle counts
        inner_count = len(terrain_mesh.inner_land_triangles) + len(terrain_mesh.inner_sea_triangles)
        outer_count = len(terrain_mesh.outer_land_triangles) + len(terrain_mesh.outer_sea_triangles)
        total_triangles = inner_count + outer_count
        print(f"  Triangles: Inner={inner_count}, Outer={outer_count}, Total={total_triangles}")
    
    avg_time = sum(generation_times) / len(generation_times)
    print(f"\n--- Performance Summary ---")
    print(f"Average generation time: {avg_time:.2f} ms")
    print(f"Fastest: {min(generation_times):.2f} ms")
    print(f"Slowest: {max(generation_times):.2f} ms")
    
    if avg_time < 100:
        print("✓ Performance is good (< 100ms)")
        return True
    elif avg_time < 200:
        print("⚠ Performance is acceptable (100-200ms)")
        return True
    else:
        print("✗ Performance needs improvement (> 200ms)")
        return False

if __name__ == "__main__":
    success = test_optimized_performance()
    sys.exit(0 if success else 1)
