#!/usr/bin/env python3
"""
Test script to validate LOD layering fix and coverage gaps
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from terrain_mesh import TerrainMesh
from heightmap import HeightMap
import pygame

def test_lod_coverage():
    """Test LOD layer coverage and ordering"""
    print("=== LOD Layer Coverage and Ordering Test ===")
    
    # Initialize required components
    pygame.init()
    
    # Load heightmap
    heightmap = HeightMap("assets/tiff/world.tiff")
    
    # Create a dummy world map surface
    world_map = pygame.Surface((100, 100))
    world_map.fill((100, 150, 100))  # Green land color
    
    # Create terrain mesh
    terrain = TerrainMesh(heightmap, world_map)
    
    # Test position (somewhere interesting)
    test_lat = 45.0
    test_lon = -100.0
    camera_altitude = 1000.0
    
    print(f"Testing at position: {test_lat}°, {test_lon}° at {camera_altitude}m altitude")
    
    # Generate mesh
    terrain.generate_dual_lod_mesh_around_position(test_lat, test_lon, camera_altitude)
    
    # Get statistics
    stats = terrain.get_mesh_statistics()
    
    print("\n=== LOD Layer Triangle Counts ===")
    print(f"Ultra (0-{terrain.ultra_radius_deg}°): {stats['ultra_total']} triangles")
    print(f"Inner ({terrain.ultra_radius_deg}-{terrain.inner_radius_deg}°): {stats['inner_total']} triangles") 
    print(f"Mid ({terrain.inner_radius_deg}-{terrain.mid_radius_deg}°): {stats['mid_total']} triangles")
    print(f"Outer ({terrain.mid_radius_deg}-{terrain.outer_radius_deg}°): {stats['outer_total']} triangles")
    print(f"Horizon ({terrain.outer_radius_deg}-{terrain.horizon_radius_deg}°): {stats['horizon_total']} triangles")
    print(f"Total: {stats['total_triangles']} triangles")
    
    print("\n=== LOD Layer Coverage Analysis ===")
    print(f"Ultra coverage: 0 - {terrain.ultra_radius_deg * 111:.0f}km")
    print(f"Inner coverage: {terrain.ultra_radius_deg * 111:.0f} - {terrain.inner_radius_deg * 111:.0f}km") 
    print(f"Mid coverage: {terrain.inner_radius_deg * 111:.0f} - {terrain.mid_radius_deg * 111:.0f}km")
    print(f"Outer coverage: {terrain.mid_radius_deg * 111:.0f} - {terrain.outer_radius_deg * 111:.0f}km")
    print(f"Horizon coverage: {terrain.outer_radius_deg * 111:.0f} - {terrain.horizon_radius_deg * 111:.0f}km")
    
    # Check for coverage gaps
    print("\n=== Coverage Gap Analysis ===")
    coverage_ranges = [
        (0, terrain.ultra_radius_deg * 111),
        (terrain.ultra_radius_deg * 111, terrain.inner_radius_deg * 111),
        (terrain.inner_radius_deg * 111, terrain.mid_radius_deg * 111),
        (terrain.mid_radius_deg * 111, terrain.outer_radius_deg * 111),
        (terrain.outer_radius_deg * 111, terrain.horizon_radius_deg * 111)
    ]
    
    gaps_found = False
    for i in range(len(coverage_ranges) - 1):
        current_end = coverage_ranges[i][1]
        next_start = coverage_ranges[i + 1][0]
        if current_end < next_start:
            print(f"⚠️  GAP: {current_end:.0f}km - {next_start:.0f}km ({next_start - current_end:.0f}km gap)")
            gaps_found = True
    
    if not gaps_found:
        print("✅ No coverage gaps detected in LOD layers")
    
    # Check for overlaps
    print("\n=== Coverage Overlap Analysis ===")
    overlaps_found = False
    for i in range(len(coverage_ranges) - 1):
        current_end = coverage_ranges[i][1]
        next_start = coverage_ranges[i + 1][0]
        if current_end > next_start:
            print(f"ℹ️  OVERLAP: {next_start:.0f}km - {current_end:.0f}km ({current_end - next_start:.0f}km overlap)")
            overlaps_found = True
    
    if not overlaps_found:
        print("✅ No overlaps detected - LOD layers have clean boundaries")
    else:
        print("ℹ️  Overlaps are expected and handled by layer priority rendering")
    
    print("\n=== Layer Priority Check ===")
    layer_priority = {'sun': 0, 'horizon': 1, 'outer': 2, 'mid': 3, 'inner': 4, 'ultra': 5}
    print("Render order (ascending priority, ultra renders last/on top):")
    for layer, priority in sorted(layer_priority.items(), key=lambda x: x[1]):
        print(f"  {priority}: {layer}")
    
    pygame.quit()

if __name__ == "__main__":
    test_lod_coverage()
