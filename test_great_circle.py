#!/usr/bin/env python3
"""Test great circle distance calculations at poles"""

import math

def great_circle_distance_km(lat1, lon1, lat2, lon2):
    """Calculate great circle distance between two points in kilometers"""
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = (math.sin(dlat/2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    earth_radius_km = 6371.0
    return earth_radius_km * c

# Test polar movement
print("Testing great circle distances at poles:")

# At North Pole, small longitude changes should be tiny distances
north_pole_tests = [
    (89.9, 0.0, 89.9, 90.0),      # 90° longitude change at near-pole
    (89.9, 0.0, 89.9, 1.0),       # 1° longitude change at near-pole  
    (89.0, 0.0, 89.0, 90.0),      # 90° longitude change at high latitude
    (40.0, 0.0, 40.0, 1.0),       # 1° longitude change at mid-latitude
]

for lat1, lon1, lat2, lon2 in north_pole_tests:
    distance = great_circle_distance_km(lat1, lon1, lat2, lon2)
    print(f"({lat1:5.1f}°, {lon1:5.1f}°) to ({lat2:5.1f}°, {lon2:5.1f}°): {distance:8.2f} km")

print("\nDegree-based vs Great Circle comparison:")
print("At 89.9°N, 90° longitude change:")
degree_diff = abs(90.0 - 0.0)  # 90° difference
gc_distance = great_circle_distance_km(89.9, 0.0, 89.9, 90.0)
print(f"  Degree difference: {degree_diff}°")
print(f"  Great circle distance: {gc_distance:.2f} km")
print(f"  Ratio: {gc_distance/degree_diff:.3f} km/degree")

print("\nAt 40°N, 1° longitude change:")
degree_diff = 1.0
gc_distance = great_circle_distance_km(40.0, 0.0, 40.0, 1.0)
print(f"  Degree difference: {degree_diff}°")
print(f"  Great circle distance: {gc_distance:.2f} km")
print(f"  Ratio: {gc_distance/degree_diff:.3f} km/degree")
