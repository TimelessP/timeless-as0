#!/usr/bin/env python3
"""Test script to validate mesh caching performance"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

import pygame
from core_simulator import get_simulator
from terrain_mesh import TerrainMesh
from heightmap import HeightMap
from main import get_assets_dir

def test_mesh_caching_performance():
    """Test mesh generation performance with caching"""
    print("Testing mesh caching performance...")
    
    # Initialize components
    pygame.init()
    assets_dir = get_assets_dir()
    world_map_path = os.path.join(assets_dir, "png", "world-map.png")
    world_map = pygame.image.load(world_map_path)
    
    simulator = get_simulator()
    heightmap = HeightMap()
    terrain_mesh = TerrainMesh(heightmap, world_map)
    
    # Test positions (small movements to test caching)
    test_positions = [
        (40.0, -74.0, 1000.0),      # NYC
        (40.01, -74.0, 1000.0),     # 1km north (should use cache)
        (40.02, -74.0, 1000.0),     # 2km north (should use cache)
        (40.1, -74.0, 1000.0),      # 11km north (should regenerate)
        (40.1, -74.01, 1000.0),     # Small move (should use cache)
        (85.0, 0.0, 1000.0),        # High latitude (different algorithm)
        (85.01, 0.0, 1000.0),       # Small polar move (should use cache)
    ]
    
    generation_times = []
    cache_hits = 0
    
    for i, (lat, lon, alt) in enumerate(test_positions):
        print(f"\nTest {i+1}: lat={lat}, lon={lon}, alt={alt}")
        
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
        
        # Check if this was likely a cache hit (very fast)
        if i > 0 and generation_time < 1.0:  # Less than 1ms suggests cache hit
            cache_hits += 1
            print(f"  ✓ Likely cache hit (fast generation)")
        
        # Get triangle counts
        inner_count = len(terrain_mesh.inner_land_triangles) + len(terrain_mesh.inner_sea_triangles)
        outer_count = len(terrain_mesh.outer_land_triangles) + len(terrain_mesh.outer_sea_triangles)
        print(f"  Triangles: Inner={inner_count}, Outer={outer_count}")
        
        # Show cache info
        print(f"  Cache size: {len(terrain_mesh.cached_meshes)} entries")
    
    # Performance summary
    print(f"\n--- Performance Summary ---")
    print(f"Total tests: {len(test_positions)}")
    print(f"Cache hits: {cache_hits}")
    print(f"Average generation time: {sum(generation_times)/len(generation_times):.2f} ms")
    print(f"Fastest generation: {min(generation_times):.2f} ms")
    print(f"Slowest generation: {max(generation_times):.2f} ms")
    print(f"Final cache size: {len(terrain_mesh.cached_meshes)} entries")
    
    if cache_hits >= 3:
        print("✓ Caching system working effectively!")
        return True
    else:
        print("⚠ Caching may not be working optimally")
        return False

if __name__ == "__main__":
    success = test_mesh_caching_performance()
    sys.exit(0 if success else 1)
