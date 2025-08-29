#!/usr/bin/env python3
"""
Test script to validate mesh calibration against heightmap resolution
"""

def main():
    print("=== Mesh Calibration Validation ===")
    print()
    
    # Heightmap resolution (from actual file inspection)
    heightmap_width = 3072
    heightmap_height = 2048
    earth_circumference_km = 40075.0
    
    # Calculate heightmap resolution
    heightmap_km_per_pixel = earth_circumference_km / heightmap_width
    heightmap_deg_per_pixel = 360.0 / heightmap_width
    
    print(f"Heightmap resolution: {heightmap_width}x{heightmap_height} pixels")
    print(f"Heightmap km per pixel at equator: {heightmap_km_per_pixel:.2f}")
    print(f"Heightmap degrees per pixel: {heightmap_deg_per_pixel:.6f}")
    print()
    
    # New mesh parameters
    inner_radius_deg = 2.0
    outer_radius_deg = 5.0
    scale_horizontal = 13050.0
    inner_resolution = 32
    outer_resolution = 16
    
    # Calculate coverage in heightmap pixels
    inner_radius_pixels = inner_radius_deg / heightmap_deg_per_pixel
    outer_radius_pixels = outer_radius_deg / heightmap_deg_per_pixel
    inner_radius_km = inner_radius_deg * (earth_circumference_km / 360.0)
    outer_radius_km = outer_radius_deg * (earth_circumference_km / 360.0)
    
    print("=== New Mesh Configuration ===")
    print(f"Inner mesh radius: {inner_radius_deg:.1f}° = {inner_radius_km:.0f} km = {inner_radius_pixels:.1f} heightmap pixels")
    print(f"Outer mesh radius: {outer_radius_deg:.1f}° = {outer_radius_km:.0f} km = {outer_radius_pixels:.1f} heightmap pixels")
    print(f"Inner mesh resolution: {inner_resolution}x{inner_resolution} vertices")
    print(f"Outer mesh resolution: {outer_resolution}x{outer_resolution} vertices")
    print()
    
    # Calculate vertex spacing
    inner_vertex_spacing_deg = (inner_radius_deg * 2) / inner_resolution
    outer_vertex_spacing_deg = (outer_radius_deg * 2) / outer_resolution
    inner_vertex_spacing_km = inner_vertex_spacing_deg * (earth_circumference_km / 360.0)
    outer_vertex_spacing_km = outer_vertex_spacing_deg * (earth_circumference_km / 360.0)
    inner_vertex_spacing_pixels = inner_vertex_spacing_deg / heightmap_deg_per_pixel
    outer_vertex_spacing_pixels = outer_vertex_spacing_deg / heightmap_deg_per_pixel
    
    print("=== Vertex Spacing Analysis ===")
    print(f"Inner mesh vertex spacing: {inner_vertex_spacing_deg:.4f}° = {inner_vertex_spacing_km:.1f} km = {inner_vertex_spacing_pixels:.1f} heightmap pixels")
    print(f"Outer mesh vertex spacing: {outer_vertex_spacing_deg:.4f}° = {outer_vertex_spacing_km:.1f} km = {outer_vertex_spacing_pixels:.1f} heightmap pixels")
    print()
    
    # Scale factor validation
    expected_scale = heightmap_km_per_pixel * 1000  # Convert km to meters
    print(f"Scale horizontal: {scale_horizontal:.0f} (expected: {expected_scale:.0f} for 1:1 heightmap pixel mapping)")
    print()
    
    # Coverage comparison
    print("=== Coverage Comparison ===")
    print(f"Previous inner radius: 0.5° = {0.5 * (earth_circumference_km / 360.0):.0f} km")
    print(f"Previous outer radius: 1.25° = {1.25 * (earth_circumference_km / 360.0):.0f} km")
    print(f"New inner radius: {inner_radius_deg}° = {inner_radius_km:.0f} km ({inner_radius_km / (0.5 * (earth_circumference_km / 360.0)):.1f}x larger)")
    print(f"New outer radius: {outer_radius_deg}° = {outer_radius_km:.0f} km ({outer_radius_km / (1.25 * (earth_circumference_km / 360.0)):.1f}x larger)")

if __name__ == "__main__":
    main()
