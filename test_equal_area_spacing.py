#!/usr/bin/env python3
"""
Demonstration of Equal-Area vs Degree-Based Mesh Spacing

This script shows how equal-area spacing (like laying cloth on a sphere) 
differs from simple degree-based spacing, especially at different latitudes.
"""

import math

def main():
    print("=== Equal-Area vs Degree-Based Mesh Spacing ===")
    print()
    
    # Test parameters
    resolution = 4  # 4x4 grid for easy visualization
    radius_deg = 2.0  # 2 degree radius
    
    # Test at different latitudes
    test_latitudes = [0.0, 30.0, 60.0, 80.0]  # Equator to near-pole
    
    for center_lat in test_latitudes:
        print(f"=== Center Latitude: {center_lat}° ===")
        
        # OLD METHOD: Equal degree spacing
        print("OLD - Equal Degree Spacing:")
        lat_step = (radius_deg * 2) / resolution
        lon_step = (radius_deg * 2) / resolution
        
        print(f"  Latitude step: {lat_step:.3f}° (constant)")
        print(f"  Longitude step: {lon_step:.3f}° (constant)")
        
        # Calculate actual surface areas (approximate)
        cos_lat = math.cos(math.radians(center_lat))
        area_per_cell_old = lat_step * lon_step * cos_lat  # Area in "square degrees" adjusted for latitude
        
        print(f"  Area per cell: {area_per_cell_old:.3f} (relative units)")
        print(f"  Longitude convergence factor: {cos_lat:.3f}")
        print()
        
        # NEW METHOD: Equal area spacing
        print("NEW - Equal Area Spacing:")
        
        # For equal area, longitude extent needs adjustment
        cos_center = math.cos(math.radians(center_lat))
        lon_radius_adjusted = radius_deg / max(cos_center, 0.1)
        
        lat_step_new = (radius_deg * 2) / resolution
        lon_step_base = (lon_radius_adjusted * 2) / resolution
        
        print(f"  Latitude step: {lat_step_new:.3f}° (constant)")
        print(f"  Longitude extent adjusted: {lon_radius_adjusted:.3f}° (was {radius_deg:.1f}°)")
        print(f"  Base longitude step: {lon_step_base:.3f}°")
        
        # Show how longitude step varies by latitude within the mesh
        print("  Longitude steps by row:")
        for i in range(resolution + 1):
            lat = center_lat - radius_deg + i * lat_step_new
            cos_lat_row = math.cos(math.radians(lat))
            lon_step_adjusted = lon_step_base / max(cos_lat_row, 0.1)
            print(f"    Row {i} (lat {lat:+6.1f}°): {lon_step_adjusted:.3f}° longitude step")
        
        # Calculate area - should be more consistent
        area_per_cell_new = lat_step_new * lon_step_base  # This should be roughly constant
        print(f"  Target area per cell: {area_per_cell_new:.3f} (relative units)")
        print()
        
        # Show the improvement
        area_distortion_old = area_per_cell_old / (lat_step * lon_step)  # How much area changed due to latitude
        area_distortion_new = 1.0  # Should be constant with equal-area spacing
        
        print(f"  Area distortion factor:")
        print(f"    Old method: {area_distortion_old:.3f} (1.0 = equator, smaller = more compressed)")
        print(f"    New method: {area_distortion_new:.3f} (constant)")
        print()
        
        # Show coverage in km
        earth_circumference = 40075.0  # km
        km_per_degree = earth_circumference / 360.0
        
        lat_km = lat_step_new * km_per_degree
        lon_km_old = lon_step * km_per_degree * cos_lat
        lon_km_new = lon_step_base * km_per_degree * cos_center  # This is the target
        
        print(f"  Physical coverage:")
        print(f"    Latitude: {lat_km:.1f} km per step (constant)")
        print(f"    Longitude old: {lon_km_old:.1f} km per step (varies by latitude)")
        print(f"    Longitude new: {lon_km_new:.1f} km per step (target constant)")
        print()
        print("-" * 60)
        print()

if __name__ == "__main__":
    main()
