"""
3D Terrain Mesh Generation for Airship Zero Observatory
Creates triangle meshes from elevation data with texture colors from world map
"""
import math
import pygame
from typing import List, Tuple, Optional, Dict, Any
from heightmap import HeightMap


class Vector3:
    """3D vector for terrain mesh vertices"""
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def dot(self, other) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def normalize(self):
        length = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        if length > 0:
            return Vector3(self.x / length, self.y / length, self.z / length)
        return Vector3(0, 0, 0)
    
    def length(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)


class TerrainVertex:
    """Vertex in 3D terrain mesh with position, normal, and texture color"""
    def __init__(self, position: Vector3, normal: Vector3, color: Tuple[int, int, int]):
        self.position = position
        self.normal = normal
        self.color = color


class TerrainTriangle:
    """Triangle in terrain mesh with three vertices"""
    def __init__(self, v1: TerrainVertex, v2: TerrainVertex, v3: TerrainVertex):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        
        # Calculate triangle normal from cross product
        edge1 = v2.position - v1.position
        edge2 = v3.position - v1.position
        self.normal = edge1.cross(edge2).normalize()
        
        # Calculate triangle center for sorting
        self.center = Vector3(
            (v1.position.x + v2.position.x + v3.position.x) / 3,
            (v1.position.y + v2.position.y + v3.position.y) / 3,
            (v1.position.z + v2.position.z + v3.position.z) / 3
        )


class Camera3D:
    """3D camera for terrain mesh rendering"""
    def __init__(self, position: Vector3, target: Vector3, up: Vector3 = None):
        self.position = position
        self.target = target
        self.up = up or Vector3(0, 0, 1)  # Z is up in our coordinate system
        
        # Calculate camera basis vectors
        self.forward = (target - position).normalize()
        self.right = self.forward.cross(self.up).normalize()
        self.up = self.right.cross(self.forward).normalize()
    
    def project_to_2d(self, world_pos: Vector3, viewport_w: int, viewport_h: int, fov_deg: float = 60.0) -> Optional[Tuple[int, int]]:
        """Project 3D world position to 2D screen coordinates with extended bounds"""
        # Transform to camera space
        relative_pos = world_pos - self.position
        
        # Camera space coordinates
        x_cam = relative_pos.dot(self.right)
        y_cam = relative_pos.dot(self.up)
        z_cam = relative_pos.dot(self.forward)
        
        # Skip points behind camera
        if z_cam <= 0:
            return None
        
        # Perspective projection
        fov_rad = math.radians(fov_deg)
        tan_half_fov = math.tan(fov_rad / 2)
        
        # Normalized device coordinates [-1, 1]
        x_ndc = x_cam / (z_cam * tan_half_fov)
        y_ndc = y_cam / (z_cam * tan_half_fov)
        
        # Convert to screen coordinates
        screen_x = int((x_ndc + 1) * viewport_w / 2)
        screen_y = int((1 - y_ndc) * viewport_h / 2)  # Flip Y for screen coordinates
        
        # Allow points well outside viewport for triangle clipping
        # Extended bounds to catch triangles that intersect viewport
        extended_margin = max(viewport_w, viewport_h)
        if (-extended_margin <= screen_x <= viewport_w + extended_margin and 
            -extended_margin <= screen_y <= viewport_h + extended_margin):
            return (screen_x, screen_y)
        
        return None
    
    def get_distance_to(self, world_pos: Vector3) -> float:
        """Get distance from camera to world position"""
        return (world_pos - self.position).length()


class TerrainMesh:
    """3D terrain mesh generator and renderer with dual-LOD system"""
    
    def __init__(self, heightmap: HeightMap, world_map: pygame.Surface):
        self.heightmap = heightmap
        self.world_map = world_map
        
        # High-detail inner mesh
        self.inner_land_triangles: List[TerrainTriangle] = []
        self.inner_sea_triangles: List[TerrainTriangle] = []
        
        # Low-detail outer mesh for extended draw distance
        self.outer_land_triangles: List[TerrainTriangle] = []
        self.outer_sea_triangles: List[TerrainTriangle] = []
        
        # Mesh parameters
        self.inner_mesh_resolution = 48  # Higher resolution for nearby terrain
        self.outer_mesh_resolution = 24  # Half resolution for distant terrain
        self.inner_radius_deg = 1.0      # Close detail radius
        self.outer_radius_deg = 3.0      # Extended draw distance
        
        self.scale_horizontal = 50000.0  # Horizontal scale in meters per degree
        self.scale_vertical = 5.0        # Realistic vertical scaling
        self.sea_level = 0.0             # Sea level in meters
        self.sea_surface_elevation = 0.0 # Sea surface at actual sea level
        self.camera_altitude = 1000.0    # Current camera altitude for culling
    
    def generate_mesh_around_position(self, center_lat: float, center_lon: float, camera_altitude: float, radius_deg: float = 3.0):
        """Generate dual-LOD terrain mesh around a central position with proper coastline handling"""
        self.inner_land_triangles.clear()
        self.inner_sea_triangles.clear()
        self.outer_land_triangles.clear()
        self.outer_sea_triangles.clear()
        self.camera_altitude = camera_altitude
        
        # Generate inner high-detail mesh
        self._generate_mesh_layer(center_lat, center_lon, camera_altitude, 
                                 self.inner_radius_deg, self.inner_mesh_resolution,
                                 self.inner_land_triangles, self.inner_sea_triangles, "inner")
        
        # Generate outer low-detail mesh
        self._generate_mesh_layer(center_lat, center_lon, camera_altitude,
                                 self.outer_radius_deg, self.outer_mesh_resolution,
                                 self.outer_land_triangles, self.outer_sea_triangles, "outer")
    
    def generate_dual_lod_mesh_around_position(self, center_lat: float, center_lon: float, 
                                             camera_altitude: float):
        """Generate dual-LOD terrain mesh around a position with seamless coastlines"""
        print(f"TerrainMesh: Generating dual-LOD mesh at {center_lat:.3f}°, {center_lon:.3f}° alt={camera_altitude:.0f}m")
        
        # Clear all triangle lists
        self.inner_land_triangles.clear()
        self.inner_sea_triangles.clear()
        self.outer_land_triangles.clear()
        self.outer_sea_triangles.clear()
        
        # Store camera altitude for proper altitude-relative rendering
        self.camera_altitude = camera_altitude
        
        # Generate inner (high-detail) mesh
        self._generate_mesh_layer(center_lat, center_lon, camera_altitude,
                                 self.inner_radius_deg, self.inner_mesh_resolution,
                                 self.inner_land_triangles, self.inner_sea_triangles, "inner")
        
        # Generate outer (low-detail) mesh  
        self._generate_mesh_layer(center_lat, center_lon, camera_altitude,
                                 self.outer_radius_deg, self.outer_mesh_resolution,
                                 self.outer_land_triangles, self.outer_sea_triangles, "outer")
        
        print(f"TerrainMesh: Generated inner mesh: {len(self.inner_land_triangles)} land, {len(self.inner_sea_triangles)} sea")
        print(f"TerrainMesh: Generated outer mesh: {len(self.outer_land_triangles)} land, {len(self.outer_sea_triangles)} sea")
    
    def _generate_mesh_layer(self, center_lat: float, center_lon: float, camera_altitude: float,
                           radius_deg: float, resolution: int, land_triangles: List[TerrainTriangle], 
                           sea_triangles: List[TerrainTriangle], layer_name: str):
        """Generate a single mesh layer with continuous coverage"""
        
        # Calculate mesh bounds with proper polar handling
        lat_min = max(-89.9, center_lat - radius_deg)
        lat_max = min(89.9, center_lat + radius_deg)
        lon_min = center_lon - radius_deg
        lon_max = center_lon + radius_deg
        
        # Handle longitude wrapping
        while lon_min < -180:
            lon_min += 360
        while lon_max > 180:
            lon_max -= 360
        
        # Create complete vertex grid (no gaps)
        vertices = {}
        step = (radius_deg * 2) / resolution
        
        # Generate all vertices in grid
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                lat = lat_min + i * step
                lon = lon_min + j * step
                
                # Handle longitude wrapping at dateline
                if lon < -180:
                    lon += 360
                elif lon > 180:
                    lon -= 360
                
                # Get elevation and color
                elevation = self.heightmap.height_at(lat, lon)
                color = self._sample_world_map_color_corrected(lat, lon)
                
                # Convert to 3D world coordinates relative to camera
                x = (lon - center_lon) * self.scale_horizontal * math.cos(math.radians(center_lat))
                y = (lat - center_lat) * self.scale_horizontal
                z = (elevation - camera_altitude) * self.scale_vertical
                
                position = Vector3(x, y, z)
                normal = self._calculate_vertex_normal(lat, lon, step * 0.1)
                
                # Determine vertex type and create appropriate vertex
                if elevation > self.sea_level:
                    # Land vertex
                    vertices[(i, j)] = TerrainVertex(position, normal, color)
                else:
                    # Sea vertex - create at sea surface
                    z_sea = (self.sea_surface_elevation - camera_altitude) * self.scale_vertical
                    position_sea = Vector3(x, y, z_sea)
                    normal_sea = Vector3(0, 0, 1)
                    sea_color = self._get_sea_color(color, elevation)
                    vertices[(i, j)] = TerrainVertex(position_sea, normal_sea, sea_color)
        
        # Generate all triangles in grid (no gaps - ensure continuous coverage)
        for i in range(resolution):
            for j in range(resolution):
                # Get all four corners of this quad
                v1 = vertices[(i, j)]
                v2 = vertices[(i + 1, j)]
                v3 = vertices[(i, j + 1)]
                v4 = vertices[(i + 1, j + 1)]
                
                # Create triangles for this quad
                triangle1 = TerrainTriangle(v1, v2, v3)
                triangle2 = TerrainTriangle(v2, v4, v3)
                
                # Determine if triangles are primarily land or sea based on vertex elevations
                quad_elevations = [
                    self.heightmap.height_at(lat_min + i * step, lon_min + j * step),
                    self.heightmap.height_at(lat_min + (i + 1) * step, lon_min + j * step),
                    self.heightmap.height_at(lat_min + i * step, lon_min + (j + 1) * step),
                    self.heightmap.height_at(lat_min + (i + 1) * step, lon_min + (j + 1) * step)
                ]
                
                # Use majority rule for triangle classification
                land_count = sum(1 for elev in quad_elevations if elev > self.sea_level)
                
                if land_count >= 2:  # Majority land
                    land_triangles.extend([triangle1, triangle2])
                else:  # Majority sea
                    sea_triangles.extend([triangle1, triangle2])
    
    def _sample_world_map_color_corrected(self, lat: float, lon: float) -> Tuple[int, int, int]:
        """Sample color from world map with correct coordinate mapping (0,0 lat/lon at center)"""
        if not self.world_map:
            return (100, 100, 100)  # Default gray
        
        # Convert lat/lon to map pixel coordinates
        map_w, map_h = self.world_map.get_size()
        
        # Handle polar regions and longitude wrapping
        lat = max(-89.9, min(89.9, lat))
        while lon < -180:
            lon += 360
        while lon > 180:
            lon -= 360
        
        # World map projection: 0,0 lat/lon should be at center of image
        # Longitude: -180 to +180 maps to 0 to map_w
        # Latitude: +90 to -90 maps to 0 to map_h (north at top)
        x_norm = (lon + 180.0) / 360.0
        y_norm = (90.0 - lat) / 180.0
        
        # Map to pixel coordinates
        map_x = int(x_norm * (map_w - 1))
        map_y = int(y_norm * (map_h - 1))
        
        # Clamp to map bounds
        map_x = max(0, min(map_w - 1, map_x))
        map_y = max(0, min(map_h - 1, map_y))
        
        try:
            color = self.world_map.get_at((map_x, map_y))
            return (color.r, color.g, color.b)
        except:
            return (100, 100, 100)  # Fallback gray
    
    def _sample_world_map_color(self, lat: float, lon: float) -> Tuple[int, int, int]:
        """Sample color from world map at given coordinates (legacy method)"""
        return self._sample_world_map_color_corrected(lat, lon)
    
    def _get_sea_color(self, base_color: Tuple[int, int, int], depth: float) -> Tuple[int, int, int]:
        """Generate appropriate sea color based on map color and depth"""
        r, g, b = base_color
        
        # Check if this looks like ocean (blue-ish) or land
        is_ocean = b > r and b > g and b > 100
        
        if is_ocean:
            # Already ocean color - darken it based on depth
            depth_factor = max(0.3, min(1.0, 1.0 + depth / 1000.0))  # Deeper = darker
            return (
                int(r * depth_factor * 0.6),  # Reduce red
                int(g * depth_factor * 0.8),  # Reduce green slightly
                int(b * depth_factor)         # Keep more blue
            )
        else:
            # Land color where sea should be - convert to ocean blue
            # Create deep ocean blue with slight variation based on original color
            base_blue = 80 + (b % 40)  # Base ocean blue with variation
            base_green = 40 + (g % 20)  # Slight green component
            base_red = 20 + (r % 15)    # Minimal red component
            
            return (base_red, base_green, base_blue)
    
    def _sample_terrain_color(self, lat: float, lon: float) -> Tuple[int, int, int]:
        """Sample color from world map at given coordinates (legacy method)"""
        return self._sample_world_map_color(lat, lon)
    
    def _calculate_vertex_normal(self, lat: float, lon: float, sample_distance: float) -> Vector3:
        """Calculate vertex normal using height samples around the point"""
        # Sample heights at surrounding points
        h_center = self.heightmap.height_at(lat, lon)
        h_north = self.heightmap.height_at(lat + sample_distance, lon)
        h_south = self.heightmap.height_at(lat - sample_distance, lon)
        h_east = self.heightmap.height_at(lat, lon + sample_distance)
        h_west = self.heightmap.height_at(lat, lon - sample_distance)
        
        # Calculate gradient vectors
        dx = (h_east - h_west) / (2 * sample_distance * self.scale_horizontal)
        dy = (h_north - h_south) / (2 * sample_distance * self.scale_horizontal)
        
        # Normal vector from cross product of tangent vectors
        tangent_x = Vector3(1, 0, dx * self.scale_vertical)
        tangent_y = Vector3(0, 1, dy * self.scale_vertical)
        normal = tangent_x.cross(tangent_y).normalize()
        
        return normal
    
    def render_to_surface(self, surface: pygame.Surface, camera: Camera3D, 
                         viewport_x: int, viewport_y: int, viewport_w: int, viewport_h: int):
        """Render dual-LOD terrain mesh to pygame surface with proper layering"""
        if not self._has_any_triangles():
            return
        
        # Combine all triangles with distance and layer information
        all_triangles = []
        
        # Add outer (distant) triangles first - render back to front
        for triangle in self.outer_sea_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'sea', 'outer', distance))
        
        for triangle in self.outer_land_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'land', 'outer', distance))
        
        # Add inner (nearby) triangles - these will be rendered on top
        for triangle in self.inner_sea_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'sea', 'inner', distance))
        
        for triangle in self.inner_land_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'land', 'inner', distance))
        
        # Sort by distance (back to front) then by layer (outer first, then inner)
        sorted_triangles = sorted(all_triangles, 
                                key=lambda t: (t[3], t[2] == 'inner'),  # Distance first, then layer priority
                                reverse=True)
        
        # Create clipping rectangle for viewport
        clip_rect = pygame.Rect(viewport_x, viewport_y, viewport_w, viewport_h)
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        
        try:
            # Render each triangle with layer-specific handling
            for triangle, triangle_type, layer, distance in sorted_triangles:
                # Skip distant triangles that are too far or behind camera
                if distance > 100000.0:  # 100km max draw distance
                    continue
                    
                self._render_triangle(surface, triangle, camera, viewport_x, viewport_y, 
                                    viewport_w, viewport_h, triangle_type, layer)
        finally:
            # Restore original clipping
            surface.set_clip(old_clip)
    
    def _has_any_triangles(self) -> bool:
        """Check if any triangles exist in either LOD level"""
        return (len(self.inner_land_triangles) > 0 or len(self.inner_sea_triangles) > 0 or
                len(self.outer_land_triangles) > 0 or len(self.outer_sea_triangles) > 0)
    
    def _render_triangle(self, surface: pygame.Surface, triangle: TerrainTriangle, camera: Camera3D,
                        viewport_x: int, viewport_y: int, viewport_w: int, viewport_h: int, 
                        triangle_type: str = 'land', layer: str = 'inner'):
        """Render a single triangle to the surface with layer and type-specific lighting"""
        # Project vertices to screen coordinates with proper clipping
        screen_coords = []
        vertices_behind_camera = 0
        valid_coords = []
        
        for vertex in [triangle.v1, triangle.v2, triangle.v3]:
            screen_pos = camera.project_to_2d(vertex.position, viewport_w, viewport_h)
            if screen_pos is None:
                vertices_behind_camera += 1
                screen_coords.append(None)  # Mark as invalid instead of placeholder
            else:
                # Offset by viewport position
                coord = (screen_pos[0] + viewport_x, screen_pos[1] + viewport_y)
                screen_coords.append(coord)
                valid_coords.append(coord)
        
        # Skip triangle if ALL vertices are behind camera
        if vertices_behind_camera >= 3:
            return
        
        # Skip if no valid coordinates
        if len(valid_coords) == 0:
            return
            
        # For partially clipped triangles, only render if we have at least 2 valid vertices
        # and they're within reasonable bounds of the viewport
        if vertices_behind_camera > 0:
            if len(valid_coords) < 2:
                return  # Can't form a meaningful triangle with less than 2 visible vertices
                
            # Check if any valid vertex is within extended viewport bounds
            viewport_bounds = pygame.Rect(viewport_x - 100, viewport_y - 100, 
                                        viewport_w + 200, viewport_h + 200)
            any_visible = False
            for coord in valid_coords:
                if viewport_bounds.collidepoint(coord):
                    any_visible = True
                    break
            
            if not any_visible:
                return
                
            # For partially clipped triangles, only use the valid coordinates
            # Skip rendering to avoid artifacts from invalid coordinates
            return
        
        # At this point, all vertices are valid - proceed with normal rendering
        final_screen_coords = [coord for coord in screen_coords if coord is not None]
        
        if len(final_screen_coords) < 3:
            return
        
        # Calculate triangle color with lighting
        if triangle_type == 'sea':
            # Sea surface lighting - more uniform, slight wave effect
            light_direction = Vector3(0.2, 0.3, 0.9).normalize()  # More vertical light
            light_intensity = max(0.7, 0.85 + 0.15 * triangle.normal.dot(light_direction))  # Higher ambient
            
            # Add slight shimmer effect for water
            shimmer = 0.05 * math.sin(triangle.center.x * 0.0005 + triangle.center.y * 0.0005)
            light_intensity = min(1.0, light_intensity + shimmer)
            
        else:
            # Land lighting - more dramatic shadows but not too dark
            light_direction = Vector3(0.5, 0.3, 0.8).normalize()  # Sunlight direction
            light_intensity = max(0.4, triangle.normal.dot(light_direction))  # Higher ambient for visibility
        
        # Use average color of vertices
        avg_color = (
            (triangle.v1.color[0] + triangle.v2.color[0] + triangle.v3.color[0]) // 3,
            (triangle.v1.color[1] + triangle.v2.color[1] + triangle.v3.color[1]) // 3,
            (triangle.v1.color[2] + triangle.v2.color[2] + triangle.v3.color[2]) // 3
        )
        
        # Apply atmospheric haze for outer layer
        if layer == 'outer':
            haze_factor = 0.25
            haze_color = (160, 180, 200)  # Light blue-grey atmospheric haze
            avg_color = (
                int(avg_color[0] * (1 - haze_factor) + haze_color[0] * haze_factor),
                int(avg_color[1] * (1 - haze_factor) + haze_color[1] * haze_factor),
                int(avg_color[2] * (1 - haze_factor) + haze_color[2] * haze_factor)
            )
            # Reduce lighting contrast for distant objects
            light_intensity = 0.6 + (light_intensity - 0.6) * 0.7
        
        # Apply lighting
        final_color = (
            int(avg_color[0] * light_intensity),
            int(avg_color[1] * light_intensity),
            int(avg_color[2] * light_intensity)
        )
        
        # Draw filled triangle only (no wireframes)
        try:
            pygame.draw.polygon(surface, final_color, final_screen_coords)
        except:
            pass  # Skip if triangle is degenerate or outside surface
    
    def get_terrain_height_at_camera(self, lat: float, lon: float) -> float:
        """Get terrain height at camera position for ground level reference"""
        return self.heightmap.height_at(lat, lon) * self.scale_vertical
    
    def get_mesh_statistics(self) -> Dict[str, Any]:
        """Get statistics about the current dual-LOD mesh for debugging"""
        return {
            "inner_land_triangles": len(self.inner_land_triangles),
            "inner_sea_triangles": len(self.inner_sea_triangles),
            "outer_land_triangles": len(self.outer_land_triangles),
            "outer_sea_triangles": len(self.outer_sea_triangles),
            "total_triangles": (len(self.inner_land_triangles) + len(self.inner_sea_triangles) + 
                               len(self.outer_land_triangles) + len(self.outer_sea_triangles)),
            "inner_total": len(self.inner_land_triangles) + len(self.inner_sea_triangles),
            "outer_total": len(self.outer_land_triangles) + len(self.outer_sea_triangles),
            "inner_mesh_resolution": self.inner_mesh_resolution,
            "outer_mesh_resolution": self.outer_mesh_resolution,
            "sea_level": self.sea_level,
            "sea_surface_elevation": self.sea_surface_elevation,
            "scale_horizontal": self.scale_horizontal,
            "scale_vertical": self.scale_vertical
        }


def create_camera_from_airship_state(game_state: Dict[str, Any], view_angle: float, 
                                   tilt_angle: float = 0.0) -> Camera3D:
    """Create 3D camera from airship position and viewing direction"""
    position_data = game_state.get("navigation", {}).get("position", {})
    current_lat = position_data.get("latitude", 0.0)
    current_lon = position_data.get("longitude", 0.0)
    current_alt = position_data.get("altitude", 1000.0)  # meters
    
    # Get ship's heading for forward reference
    ship_heading = position_data.get("heading", 0.0)
    
    # Camera position (airship position in world coordinates)
    camera_pos = Vector3(0, 0, 0)  # Camera at origin (airship position)
    
    # Calculate target position based on view angle
    # view_angle 0 should look forward (ship's heading)
    # Mouse at center should point toward ship's forward direction
    actual_look_angle = ship_heading + view_angle
    
    view_distance = 20000.0  # Look distance in meters
    target_x = view_distance * math.sin(math.radians(actual_look_angle))
    target_y = view_distance * math.cos(math.radians(actual_look_angle))
    target_z = view_distance * math.tan(math.radians(tilt_angle))
    
    target_pos = Vector3(target_x, target_y, target_z)
    
    return Camera3D(camera_pos, target_pos)
