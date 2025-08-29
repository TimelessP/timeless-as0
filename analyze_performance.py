#!/usr/bin/env python3
"""
Performance analysis script for terrain mesh rendering
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from terrain_mesh import TerrainMesh
from heightmap import HeightMap
import pygame
import time

def analyze_performance():
    """Analyze current terrain mesh performance"""
    print("=== Terrain Mesh Performance Analysis ===")
    
    # Initialize required components
    pygame.init()
    
    # Load heightmap
    heightmap = HeightMap("assets/tiff/world.tiff")
    
    # Create a dummy world map surface
    world_map = pygame.Surface((100, 100))
    world_map.fill((100, 150, 100))
    
    # Create terrain mesh
    terrain = TerrainMesh(heightmap, world_map)
    
    # Test position
    test_lat = 45.0
    test_lon = -100.0
    camera_altitude = 1000.0
    
    print(f"Testing at position: {test_lat}°, {test_lon}° at {camera_altitude}m altitude")
    
    # Time mesh generation
    start_time = time.time()
    terrain.generate_dual_lod_mesh_around_position(test_lat, test_lon, camera_altitude)
    generation_time = time.time() - start_time
    
    # Get statistics
    stats = terrain.get_mesh_statistics()
    
    print(f"\n=== Performance Results ===")
    print(f"Mesh generation time: {generation_time*1000:.1f}ms")
    print(f"Total triangles: {stats['total_triangles']:,}")
    print(f"Triangles per LOD level:")
    print(f"  Ultra:   {stats['ultra_total']:,} triangles ({stats['ultra_mesh_resolution']}² grid)")
    print(f"  Inner:   {stats['inner_total']:,} triangles ({stats['inner_mesh_resolution']}² grid)")
    print(f"  Mid:     {stats['mid_total']:,} triangles ({stats['mid_mesh_resolution']}² grid)")
    print(f"  Outer:   {stats['outer_total']:,} triangles ({stats['outer_mesh_resolution']}² grid)")
    print(f"  Horizon: {stats['horizon_total']:,} triangles ({stats['horizon_mesh_resolution']}² grid)")
    
    # Calculate theoretical triangles per resolution
    print(f"\n=== Triangle Density Analysis ===")
    for layer in ['ultra', 'inner', 'mid', 'outer', 'horizon']:
        resolution = stats[f'{layer}_mesh_resolution']
        theoretical = resolution * resolution * 2  # 2 triangles per grid cell
        actual = stats[f'{layer}_total']
        print(f"{layer.capitalize():>7}: {resolution:2}² = {theoretical:,} theoretical, {actual:,} actual")
    
    # Performance projections
    estimated_60fps_budget = 16.67  # milliseconds per frame at 60fps
    triangles_per_ms = stats['total_triangles'] / (generation_time * 1000) if generation_time > 0 else 0
    
    print(f"\n=== Performance Analysis ===")
    print(f"Generation rate: {triangles_per_ms:,.0f} triangles/ms")
    if generation_time > 0:
        theoretical_60fps_triangles = triangles_per_ms * estimated_60fps_budget
        print(f"60fps triangle budget: ~{theoretical_60fps_triangles:,.0f} triangles")
        if stats['total_triangles'] > theoretical_60fps_triangles:
            print(f"⚠️  Current load ({stats['total_triangles']:,}) exceeds 60fps budget")
            reduction_needed = stats['total_triangles'] / theoretical_60fps_triangles
            print(f"   Need {reduction_needed:.1f}x triangle reduction for 60fps")
        else:
            print(f"✅ Current load within 60fps budget")
    
    # Coverage analysis
    print(f"\n=== Coverage Analysis ===")
    for layer in ['ultra', 'inner', 'mid', 'outer', 'horizon']:
        radius_km = stats[f'{layer}_radius_deg'] * 111  # rough conversion
        print(f"{layer.capitalize():>7}: {radius_km:7.0f}km radius")
    
    pygame.quit()

if __name__ == "__main__":
    analyze_performance()
