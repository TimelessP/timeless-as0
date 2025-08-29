"""
3D Terrain Mesh Generation for Airship Zero Observatory
Creates triangle meshes from elevation data with texture colors from world map
"""
import math
import pygame
from typing import List, Tuple, Optional, Dict, Any
from heightmap import HeightMap

# Debug mode for tracking rare edge cases
DEBUG_SKY_FILLING = False  # Disabled after confirming it works
DEBUG_CULLING = False
# Special tracking for rare edge cases that slip through
TRACK_EDGE_CASES = False


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
    
    def __str__(self):
        return f"({self.x:.1f}, {self.y:.1f}, {self.z:.1f})"


class TerrainVertex:
    """Vertex in 3D terrain mesh with position, normal, and texture color"""
    def __init__(self, position: Vector3, normal: Vector3, color: Tuple[int, int, int], lat: float = 0.0, lon: float = 0.0):
        self.position = position
        self.normal = normal
        self.color = color
        self.lat = lat
        self.lon = lon


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
        """Project 3D world position to 2D screen coordinates"""
        # Transform to camera space
        relative_pos = world_pos - self.position
        
        # Camera space coordinates
        x_cam = relative_pos.dot(self.right)
        y_cam = relative_pos.dot(self.up)
        z_cam = relative_pos.dot(self.forward)
        
        # Calculate distance to vertex
        distance = relative_pos.length()
        
        # Proper view frustum culling instead of distance-based protection
        # Define the view frustum parameters
        fov_rad = math.radians(fov_deg)
        tan_half_fov = math.tan(fov_rad / 2)
        aspect_ratio = viewport_w / viewport_h
        
        # Near and far plane distances
        near_plane = 1.0  # Very close near plane for ground terrain
        far_plane = 50000.0  # Far plane
        
        # Check if vertex is within the view frustum (with generous margins for triangle clipping)
        def is_in_view_frustum_generous(x_cam, y_cam, z_cam, margin_multiplier=2.0):
            # Must be in front of near plane and behind far plane
            if z_cam < near_plane or z_cam > far_plane:
                return False
            
            # Calculate frustum bounds at this z distance with generous margins
            frustum_half_height = z_cam * tan_half_fov * margin_multiplier
            frustum_half_width = frustum_half_height * aspect_ratio
            
            # Check if within expanded horizontal and vertical frustum bounds
            if abs(x_cam) > frustum_half_width or abs(y_cam) > frustum_half_height:
                return False
                
            return True
        
        # For close terrain, be very permissive to ensure triangle edges are captured
        triangle_edge_distance = 470.0  # Distance between triangle centers in ultra mesh
        close_terrain_radius = triangle_edge_distance * 3.0  # 3 triangle lengths
        
        # For ALL terrain, use proper frustum culling
        if not is_in_view_frustum_generous(x_cam, y_cam, z_cam, margin_multiplier=4.0):
            return None
        
        # Perspective projection with aspect ratio correction
        fov_rad = math.radians(fov_deg)
        tan_half_fov = math.tan(fov_rad / 2)
        aspect_ratio = viewport_w / viewport_h
        
        # Proper near plane handling - do not project vertices behind camera
        if z_cam < near_plane:
            return None  # Vertex is behind near plane, should be clipped at triangle level
        
        # Normalized device coordinates [-1, 1] with aspect ratio correction
        x_ndc = x_cam / (z_cam * tan_half_fov * aspect_ratio)
        y_ndc = y_cam / (z_cam * tan_half_fov)
        
        # Convert to screen coordinates
        screen_x = int((x_ndc + 1) * viewport_w / 2)
        screen_y = int((1 - y_ndc) * viewport_h / 2)  # Flip Y for screen coordinates
        
        # For ALL terrain, use generous viewport bounds to allow triangle clipping
        # Use reasonable margins to ensure triangle edges are captured
        extended_margin = max(viewport_w, viewport_h) * 2  # 2x margin for triangle clipping
        
        # Only cull if well outside the viewport to allow proper triangle clipping
        if (screen_x < -extended_margin or screen_x > viewport_w + extended_margin or
            screen_y < -extended_margin or screen_y > viewport_h + extended_margin):
            return None
            
        return (screen_x, screen_y)
    
    def get_distance_to(self, world_pos: Vector3) -> float:
        """Get distance from camera to world position"""
        return (world_pos - self.position).length()
    
    def clip_triangle_near_plane(self, triangle_vertices, near_plane=1.0):
        """
        Clip a triangle against the near plane, returning clipped triangle(s)
        Returns a list of triangle vertex lists (each with 3 vertices)
        """
        vertices = triangle_vertices[:]  # Copy the list
        
        # Transform vertices to camera space to check Z values
        cam_vertices = []
        for vertex in vertices:
            relative_pos = vertex.position - self.position
            z_cam = relative_pos.dot(self.forward)
            cam_vertices.append((vertex, z_cam))
        
        # Check which vertices are in front of near plane
        front_vertices = [(v, z) for v, z in cam_vertices if z >= near_plane]
        back_vertices = [(v, z) for v, z in cam_vertices if z < near_plane]
        
        # If all vertices are in front, no clipping needed
        if len(back_vertices) == 0:
            return [vertices]
        
        # If all vertices are behind, triangle is completely clipped
        if len(front_vertices) == 0:
            return []
        
        # If 1 or 2 vertices are behind near plane, we need to clip
        # For now, just reject the triangle - proper clipping is complex
        # This prevents the projection instability without visual artifacts
        return []


class TerrainMesh:
    """3D terrain mesh generator and renderer with dual-LOD system"""
    
    def __init__(self, heightmap: HeightMap, world_map: pygame.Surface):
        self.heightmap = heightmap
        self.world_map = world_map
        
        # Multi-tier LOD mesh system for extended draw distance
        # Ultra-high detail (immediate vicinity)
        self.ultra_land_triangles: List[TerrainTriangle] = []
        self.ultra_sea_triangles: List[TerrainTriangle] = []
        
        # High-detail inner mesh
        self.inner_land_triangles: List[TerrainTriangle] = []
        self.inner_sea_triangles: List[TerrainTriangle] = []
        
        # Medium-detail mid-range mesh
        self.mid_land_triangles: List[TerrainTriangle] = []
        self.mid_sea_triangles: List[TerrainTriangle] = []
        
        # Low-detail outer mesh
        self.outer_land_triangles: List[TerrainTriangle] = []
        self.outer_sea_triangles: List[TerrainTriangle] = []
        
        # Ultra-low detail horizon mesh
        self.horizon_land_triangles: List[TerrainTriangle] = []
        self.horizon_sea_triangles: List[TerrainTriangle] = []
        
        # 3D sun mesh
        self.sun_triangles: List[TerrainTriangle] = []
        
        # Multi-tier LOD mesh parameters for extended draw distance with performance
        # Heightmap resolution: 0.117188 degrees per pixel at equator (13.05 km per pixel)
        
        # Ultra-high detail (immediate vicinity)
        self.ultra_mesh_resolution = 28   # Reduced from 32 for performance
        self.ultra_radius_deg = 1.0       # ~111km radius - extended immediate area
        
        # High detail (close terrain)
        self.inner_mesh_resolution = 20   # Reduced from 24 for performance
        self.inner_radius_deg = 1.2       # ~133km radius - close detail
        
        # Medium detail (mid-range)
        self.mid_mesh_resolution = 14     # Reduced from 16 for performance
        self.mid_radius_deg = 3.0         # ~333km radius - mid-range view
        
        # Low detail (distant terrain)
        self.outer_mesh_resolution = 10   # Reduced from 12 for performance
        self.outer_radius_deg = 8.0       # ~889km radius - extended draw distance
        
        # Ultra-low detail (horizon)
        self.horizon_mesh_resolution = 6  # Reduced from 8 for performance
        self.horizon_radius_deg = 15.0    # ~1667km radius - horizon visibility
        
        # Scale calibrated to heightmap pixel width at equator: 13.05 km per pixel
        # This ensures mesh vertex spacing matches the maximum resolution of our source data
        self.scale_horizontal = 13050.0  # Horizontal scale factor (13.05 km per heightmap pixel)
        self.scale_vertical = 0.15       # Reduced vertical exaggeration for realistic proportions from altitude
        self.sea_level = 0.0             # Sea level in meters
        self.sea_surface_elevation = 0.0 # Sea surface at actual sea level
        self.camera_altitude = 1000.0    # Current camera altitude for culling
        
        # Mesh caching system for performance - more aggressive caching
        self.cached_meshes = {}  # Key: (lat_grid, lon_grid, alt_grid), Value: mesh data
        self.cache_grid_size = 0.03  # Slightly larger cache grid (~3.3km) for better hit rate
        self.cache_invalidation_distance_km = 1.2  # More aggressive caching - cache longer
        self.last_cache_position = None
        
        # Sun caching system (sun changes very slowly)
        self.cached_sun_triangles = []
        self.last_sun_generation_time = 0
        self.sun_cache_duration_minutes = 10  # Regenerate sun every 10 minutes
        
        # Debug frame counter to limit debug output
        self.debug_frame_counter = 0
        self.sky_fill_events_this_frame = 0
        self.large_triangles_this_frame = 0  # Track unusually large triangles
        
        # Track unique large triangles to avoid spam
        self.logged_large_triangles = set()
    
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
        """Generate multi-tier LOD terrain mesh around a position with caching for performance"""
        
        # Check if we can use cached mesh
        cache_key = self._get_cache_key(center_lat, center_lon, camera_altitude)
        
        # Check if we need to regenerate based on movement
        current_pos = (center_lat, center_lon, camera_altitude)
        if (self.last_cache_position is not None and 
            self._should_use_cache(current_pos, self.last_cache_position)):
            # Use cached mesh if available
            if cache_key in self.cached_meshes:
                cached_data = self.cached_meshes[cache_key]
                self.ultra_land_triangles = cached_data.get('ultra_land', []).copy()
                self.ultra_sea_triangles = cached_data.get('ultra_sea', []).copy()
                self.inner_land_triangles = cached_data['inner_land'].copy()
                self.inner_sea_triangles = cached_data['inner_sea'].copy()
                self.mid_land_triangles = cached_data.get('mid_land', []).copy()
                self.mid_sea_triangles = cached_data.get('mid_sea', []).copy()
                self.outer_land_triangles = cached_data['outer_land'].copy()
                self.outer_sea_triangles = cached_data['outer_sea'].copy()
                self.horizon_land_triangles = cached_data.get('horizon_land', []).copy()
                self.horizon_sea_triangles = cached_data.get('horizon_sea', []).copy()
                self.camera_altitude = camera_altitude
                return
        
        # Generate new multi-tier mesh
        self.ultra_land_triangles.clear()
        self.ultra_sea_triangles.clear()
        self.inner_land_triangles.clear()
        self.inner_sea_triangles.clear()
        self.mid_land_triangles.clear()
        self.mid_sea_triangles.clear()
        self.outer_land_triangles.clear()
        self.outer_sea_triangles.clear()
        self.horizon_land_triangles.clear()
        self.horizon_sea_triangles.clear()
        
        # Store camera altitude for proper altitude-relative rendering
        self.camera_altitude = camera_altitude
        
        # Generate all LOD levels with adaptive detail based on distance
        # Ultra-high detail for immediate vicinity (landing, close terrain inspection)
        self._generate_mesh_layer_optimized(center_lat, center_lon, camera_altitude,
                                           self.ultra_radius_deg, self.ultra_mesh_resolution,
                                           self.ultra_land_triangles, self.ultra_sea_triangles, "ultra")
        
        # High detail for close terrain
        self._generate_mesh_layer_optimized(center_lat, center_lon, camera_altitude,
                                           self.inner_radius_deg, self.inner_mesh_resolution,
                                           self.inner_land_triangles, self.inner_sea_triangles, "inner")
        
        # Medium detail for mid-range terrain
        self._generate_mesh_layer_optimized(center_lat, center_lon, camera_altitude,
                                           self.mid_radius_deg, self.mid_mesh_resolution,
                                           self.mid_land_triangles, self.mid_sea_triangles, "mid")
        
        # Low detail for distant terrain
        self._generate_mesh_layer_optimized(center_lat, center_lon, camera_altitude,
                                           self.outer_radius_deg, self.outer_mesh_resolution,
                                           self.outer_land_triangles, self.outer_sea_triangles, "outer")
        
        # Ultra-low detail for horizon
        self._generate_mesh_layer_optimized(center_lat, center_lon, camera_altitude,
                                           self.horizon_radius_deg, self.horizon_mesh_resolution,
                                           self.horizon_land_triangles, self.horizon_sea_triangles, "horizon")
        
        # Cache the generated mesh with all LOD levels
        self.cached_meshes[cache_key] = {
            'ultra_land': self.ultra_land_triangles.copy(),
            'ultra_sea': self.ultra_sea_triangles.copy(),
            'inner_land': self.inner_land_triangles.copy(),
            'inner_sea': self.inner_sea_triangles.copy(),
            'mid_land': self.mid_land_triangles.copy(),
            'mid_sea': self.mid_sea_triangles.copy(),
            'outer_land': self.outer_land_triangles.copy(),
            'outer_sea': self.outer_sea_triangles.copy(),
            'horizon_land': self.horizon_land_triangles.copy(),
            'horizon_sea': self.horizon_sea_triangles.copy()
        }
        
        # Update last cache position
        self.last_cache_position = current_pos
        
        # Limit cache size to prevent memory growth (smaller limit due to more data per cache)
        if len(self.cached_meshes) > 15:  # Reduced from 25 due to more triangles per cache
            oldest_key = next(iter(self.cached_meshes))
            del self.cached_meshes[oldest_key]
    
    def _get_cache_key(self, lat: float, lon: float, alt: float) -> tuple:
        """Generate cache key based on position grid"""
        lat_grid = round(lat / self.cache_grid_size) * self.cache_grid_size
        lon_grid = round(lon / self.cache_grid_size) * self.cache_grid_size
        alt_grid = round(alt / 100) * 100  # 100m altitude grid
        return (lat_grid, lon_grid, alt_grid)
    
    def _should_use_cache(self, current_pos: tuple, last_pos: tuple) -> bool:
        """Check if current position is close enough to use cached mesh using great circle distance"""
        return self._great_circle_distance_km(current_pos[0], current_pos[1], 
                                             last_pos[0], last_pos[1]) < self.cache_invalidation_distance_km
    
    def _great_circle_distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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
    
    def _generate_mesh_layer_optimized(self, center_lat: float, center_lon: float, camera_altitude: float,
                                     radius_deg: float, resolution: int, land_triangles: List[TerrainTriangle], 
                                     sea_triangles: List[TerrainTriangle], layer_name: str):
        """Generate mesh layer with optimized coordinate calculations for performance"""
        
        # Pre-calculate trigonometric values
        center_lat_rad = math.radians(center_lat)
        center_lon_rad = math.radians(center_lon)
        cos_center_lat = math.cos(center_lat_rad)
        
        # Use simple rectangular grid for non-polar regions (|lat| < 85°)
        # This is much faster than full spherical calculations
        if abs(center_lat) < 85.0:
            return self._generate_mesh_rectangular(center_lat, center_lon, camera_altitude,
                                                 radius_deg, resolution, land_triangles, 
                                                 sea_triangles, layer_name)
        else:
            # Use full spherical geometry only near poles
            return self._generate_mesh_layer(center_lat, center_lon, camera_altitude,
                                           radius_deg, resolution, land_triangles, 
                                           sea_triangles, layer_name)
    
    def _generate_mesh_rectangular(self, center_lat: float, center_lon: float, camera_altitude: float,
                                 radius_deg: float, resolution: int, land_triangles: List[TerrainTriangle], 
                                 sea_triangles: List[TerrainTriangle], layer_name: str):
        """True equal-area mesh generation - 'cloth wrapped on sphere' implementation"""
        
        # Convert radius to actual surface distance for equal-area calculation
        earth_radius_km = 6371.0
        radius_km = math.radians(radius_deg) * earth_radius_km
        total_area_km2 = math.pi * radius_km * radius_km  # Circle area on sphere surface
        cell_area_km2 = total_area_km2 / (resolution * resolution)  # Target area per cell
        cell_size_km = math.sqrt(cell_area_km2)  # Target cell side length
        
        # Generate vertices in equal-area grid
        vertices = {}
        center_lat_rad = math.radians(center_lat)
        center_lon_rad = math.radians(center_lon)
        
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                # Calculate position in equal-area grid
                # Move from center in steps that maintain equal surface area
                u = (i - resolution/2) / resolution  # -0.5 to +0.5
                v = (j - resolution/2) / resolution  # -0.5 to +0.5
                
                # Convert to surface distance (km) from center
                x_km = u * radius_km * 2  # -radius_km to +radius_km
                y_km = v * radius_km * 2  # -radius_km to +radius_km
                
                # Convert local surface coordinates to lat/lon using proper spherical geometry
                # This ensures equal area regardless of latitude
                angular_x = x_km / earth_radius_km  # radians
                angular_y = y_km / earth_radius_km  # radians
                
                # Apply spherical coordinate transformation
                lat_rad = center_lat_rad + angular_y
                # Longitude adjustment for spherical surface (more complex near poles)
                cos_lat = math.cos(lat_rad)
                if abs(cos_lat) > 0.01:  # Not too close to poles
                    lon_rad = center_lon_rad + angular_x / cos_lat
                else:
                    lon_rad = center_lon_rad  # At poles, longitude is undefined
                
                lat = math.degrees(lat_rad)
                lon = math.degrees(lon_rad)
                
                # Handle coordinate wrapping
                lat = max(-89.99, min(89.99, lat))
                while lon < -180:
                    lon += 360
                while lon > 180:
                    lon -= 360
                
                # Get elevation and color
                elevation = self.heightmap.height_at(lat, lon)
                color = self._sample_world_map_color_corrected(lat, lon)
                
                # Convert to 3D coordinates for rendering
                # Use the local surface coordinates for consistent scaling
                x = x_km * self.scale_horizontal / 1000.0  # Convert km to scaled units
                y = y_km * self.scale_horizontal / 1000.0
                z = (elevation - camera_altitude) * self.scale_vertical
                
                position = Vector3(x, y, z)
                normal = self._calculate_vertex_normal_fast(lat, lon, cell_size_km / earth_radius_km)
                
                # Create vertex
                if elevation > self.sea_level:
                    vertices[(i, j)] = TerrainVertex(position, normal, color, lat, lon)
                else:
                    z_sea = (self.sea_surface_elevation - camera_altitude) * self.scale_vertical
                    position_sea = Vector3(x, y, z_sea)
                    normal_sea = Vector3(0, 0, 1)
                    sea_color = self._get_sea_color(color, elevation)
                    vertices[(i, j)] = TerrainVertex(position_sea, normal_sea, sea_color, lat, lon)
        
        # Generate triangles (same as before)
        for i in range(resolution):
            for j in range(resolution):
                v1 = vertices[(i, j)]
                v2 = vertices[(i + 1, j)]
                v3 = vertices[(i, j + 1)]
                v4 = vertices[(i + 1, j + 1)]
                
                triangle1 = TerrainTriangle(v1, v2, v3)
                triangle2 = TerrainTriangle(v2, v4, v3)
                
                self._update_triangle_color_from_centroid(triangle1, center_lat, center_lon)
                self._update_triangle_color_from_centroid(triangle2, center_lat, center_lon)
                
                # Classify triangles
                quad_elevations = [
                    self.heightmap.height_at(v1.lat, v1.lon),
                    self.heightmap.height_at(v2.lat, v2.lon), 
                    self.heightmap.height_at(v3.lat, v3.lon),
                    self.heightmap.height_at(v4.lat, v4.lon)
                ]
                
                land_count = sum(1 for elev in quad_elevations if elev > self.sea_level)
                
                if land_count >= 2:
                    land_triangles.extend([triangle1, triangle2])
                else:
                    sea_triangles.extend([triangle1, triangle2])
    
    def _calculate_vertex_normal_fast(self, lat: float, lon: float, sample_distance: float) -> Vector3:
        """Ultra-fast vertex normal calculation optimized for performance"""
        # For performance at altitude, use simplified terrain-aware normals
        # Sample only 2 points instead of 4 for major performance gain
        h_center = self.heightmap.height_at(lat, lon)
        h_east = self.heightmap.height_at(lat, lon + sample_distance)
        h_north = self.heightmap.height_at(min(89.9, lat + sample_distance), lon)
        
        # Calculate simple gradient
        dx = (h_east - h_center) / (sample_distance * self.scale_horizontal)
        dy = (h_north - h_center) / (sample_distance * self.scale_horizontal)
        
        # Simple normal from gradient - much faster than cross product
        normal_magnitude = math.sqrt(dx*dx + dy*dy + 1.0)
        return Vector3(-dx/normal_magnitude, -dy/normal_magnitude, 1.0/normal_magnitude)
    
    def generate_3d_sun(self, observer_lat: float, observer_lon: float, observer_alt: float, 
                       time_info: dict):
        """Generate 3D sun mesh based on astronomical position with caching"""
        import time
        import datetime
        
        # Check if we can use cached sun triangles
        current_time = time.time()
        if (self.cached_sun_triangles and 
            (current_time - self.last_sun_generation_time) < (self.sun_cache_duration_minutes * 60)):
            # Use cached sun triangles
            self.sun_triangles = self.cached_sun_triangles.copy()
            return
        
        # Clear existing sun triangles
        self.sun_triangles.clear()
        
        # Calculate sun's subsolar point (where sun is directly overhead on Earth)
        utc_time = time.gmtime()
        utc_hours = utc_time.tm_hour + utc_time.tm_min / 60.0 + utc_time.tm_sec / 3600.0
        utc_date = datetime.date(utc_time.tm_year, utc_time.tm_mon, utc_time.tm_mday)
        
        # Solar longitude (15 degrees per hour westward from Greenwich)
        subsolar_lon = -15.0 * (utc_hours - 12.0)
        subsolar_lon = ((subsolar_lon + 180) % 360) - 180  # Normalize to [-180, 180]
        
        # Solar latitude based on Earth's axial tilt and day of year
        max_declination = 23.44  # Earth's axial tilt in degrees
        day_of_year = utc_date.timetuple().tm_yday
        
        # Summer solstice is approximately day 172 (June 21st)
        declination_angle = (day_of_year - 172) * (2 * math.pi / 365.25)
        subsolar_lat = max_declination * math.cos(declination_angle)
        
        # Calculate sun's position in local sky coordinates
        sun_elevation, sun_azimuth = self._calculate_sun_elevation_azimuth(
            observer_lat, observer_lon, subsolar_lat, subsolar_lon)
        
        # Only generate sun if it's above horizon
        if sun_elevation <= 0:
            return  # Sun is below horizon
        
        # Calculate 3D position for sun in absolute world coordinates
        sun_distance = 10000.0  # 10km away for rendering purposes
        
        # Convert spherical coordinates to 3D position in absolute world space
        elevation_rad = math.radians(sun_elevation)
        azimuth_rad = math.radians(sun_azimuth)
        
        # Calculate sun position in absolute world coordinates (North=+Y, East=+X, Up=+Z)
        # Azimuth 0° = North, 90° = East, 180° = South, 270° = West
        sun_x = sun_distance * math.sin(azimuth_rad) * math.cos(elevation_rad)  # East/West
        sun_y = sun_distance * math.cos(azimuth_rad) * math.cos(elevation_rad)  # North/South
        sun_z = sun_distance * math.sin(elevation_rad)  # Up/Down
        
        sun_center = Vector3(sun_x, sun_y, sun_z)
        
        # Calculate sun color based on elevation (white high, orange near horizon)
        sun_color = self._calculate_sun_color(sun_elevation)
        
        # Generate 12-sided polygon (dodecagon) made of triangles
        # Make sun larger than realistic for better visibility in game
        angular_radius_deg = 2.0  # Much larger than real sun's 0.25° for game visibility
        angular_radius_rad = math.radians(angular_radius_deg)
        sun_radius = sun_distance * math.tan(angular_radius_rad)  # Game-sized for visibility
        self._generate_sun_dodecagon(sun_center, sun_radius, sun_color, elevation_rad, azimuth_rad)
        
        # Cache the generated sun triangles and update timestamp
        self.cached_sun_triangles = self.sun_triangles.copy()
        self.last_sun_generation_time = current_time
    
    def _local_cartesian_to_latlon(self, local_x_km: float, local_y_km: float, 
                                  center_lat: float, center_lon: float) -> Tuple[float, float]:
        """Convert local Cartesian coordinates (km) to lat/lon using spherical geometry"""
        earth_radius_km = 6371.0
        
        # Convert local distances to angular distances
        angular_x = local_x_km / earth_radius_km  # radians
        angular_y = local_y_km / earth_radius_km  # radians
        
        center_lat_rad = math.radians(center_lat)
        center_lon_rad = math.radians(center_lon)
        
        # For small distances, we can use approximate flat-earth transformation
        # This is valid for mesh generation within ~100km of our position
        lat_rad = center_lat_rad + angular_y
        lon_rad = center_lon_rad + angular_x / math.cos(center_lat_rad) if abs(center_lat) < 89 else center_lon_rad
        
        # Convert back to degrees
        lat = math.degrees(lat_rad)
        lon = math.degrees(lon_rad)
        
        return lat, lon
    
    def _calculate_sun_elevation_azimuth(self, observer_lat: float, observer_lon: float, 
                                       subsolar_lat: float, subsolar_lon: float) -> Tuple[float, float]:
        """Calculate sun's elevation and azimuth from observer position"""
        # Convert to radians
        obs_lat_rad = math.radians(observer_lat)
        obs_lon_rad = math.radians(observer_lon)
        sun_lat_rad = math.radians(subsolar_lat)
        sun_lon_rad = math.radians(subsolar_lon)
        
        # Calculate angular distance between observer and subsolar point
        dlon = sun_lon_rad - obs_lon_rad
        
        # Calculate sun elevation using spherical trigonometry
        sin_elevation = (math.sin(obs_lat_rad) * math.sin(sun_lat_rad) + 
                        math.cos(obs_lat_rad) * math.cos(sun_lat_rad) * math.cos(dlon))
        elevation = math.degrees(math.asin(max(-1, min(1, sin_elevation))))
        
        # Calculate sun azimuth
        if math.cos(sun_lat_rad) == 0:
            azimuth = 180.0 if subsolar_lat > observer_lat else 0.0
        else:
            sin_azimuth = math.sin(dlon) * math.cos(sun_lat_rad) / math.cos(math.radians(elevation))
            cos_azimuth = ((math.sin(sun_lat_rad) - math.sin(obs_lat_rad) * math.sin(math.radians(elevation))) /
                          (math.cos(obs_lat_rad) * math.cos(math.radians(elevation))))
            
            azimuth = math.degrees(math.atan2(sin_azimuth, cos_azimuth))
            azimuth = (azimuth + 360) % 360  # Normalize to 0-360
        
        return elevation, azimuth
    
    def _calculate_sun_color(self, elevation: float) -> Tuple[int, int, int]:
        """Calculate sun color based on elevation angle"""
        # White at high elevations, orange near horizon
        # Non-linear transition kicks in as it approaches horizon
        
        if elevation >= 60:
            # High in sky - pure white
            return (255, 255, 255)
        elif elevation >= 30:
            # Medium height - slight warmth
            factor = (elevation - 30) / 30  # 0 to 1
            return (255, int(255 * (0.9 + 0.1 * factor)), int(255 * (0.8 + 0.2 * factor)))
        elif elevation >= 10:
            # Getting lower - more orange
            factor = (elevation - 10) / 20  # 0 to 1
            return (255, int(255 * (0.7 + 0.2 * factor)), int(255 * (0.4 + 0.4 * factor)))
        else:
            # Near horizon - deep orange
            factor = max(0, elevation / 10)  # 0 to 1
            return (255, int(255 * (0.5 + 0.2 * factor)), int(255 * (0.2 + 0.2 * factor)))
    
    def _generate_sun_dodecagon(self, center: Vector3, radius: float, color: Tuple[int, int, int],
                              elevation_rad: float, azimuth_rad: float):
        """Generate 12-sided sun polygon made of triangles"""
        # Create 12 vertices around the center in a plane perpendicular to view direction
        vertices = []
        
        # Create local coordinate system for the sun plane
        # Sun faces toward observer
        forward = Vector3(-math.sin(azimuth_rad) * math.cos(elevation_rad),
                         -math.cos(azimuth_rad) * math.cos(elevation_rad),
                         -math.sin(elevation_rad)).normalize()
        
        # Create perpendicular vectors for the sun plane
        up = Vector3(0, 0, 1)  # World up
        right = forward.cross(up).normalize()
        plane_up = right.cross(forward).normalize()
        
        # Generate 12 vertices in a circle
        for i in range(12):
            angle = i * 2 * math.pi / 12
            local_x = radius * math.cos(angle)
            local_y = radius * math.sin(angle)
            
            # Transform to world coordinates
            vertex_pos = center + right * local_x + plane_up * local_y
            # Normal points toward observer (same as forward direction)
            vertex_normal = forward
            vertex = TerrainVertex(vertex_pos, vertex_normal, color, 0.0, 0.0)  # Sun uses default lat/lon
            vertices.append(vertex)
        
        # Create triangles from center to each edge (12 triangles total)
        center_vertex = TerrainVertex(center, forward, color)
        
        for i in range(12):
            next_i = (i + 1) % 12
            triangle = TerrainTriangle(center_vertex, vertices[i], vertices[next_i])
            self.sun_triangles.append(triangle)
    
    def _generate_mesh_layer(self, center_lat: float, center_lon: float, camera_altitude: float,
                           radius_deg: float, resolution: int, land_triangles: List[TerrainTriangle], 
                           sea_triangles: List[TerrainTriangle], layer_name: str):
        """Generate a single mesh layer with equal-area coverage using proper spherical geometry"""
        
        # Create complete vertex grid using equal-area spacing
        vertices = {}
        
        # Convert radius from degrees to actual surface distance (km)
        earth_radius_km = 6371.0
        radius_km = math.radians(radius_deg) * earth_radius_km
        
        # Generate vertices in equal-area grid (like laying cloth on sphere surface)
        # Each grid cell covers the same physical area regardless of latitude
        step_km = (radius_km * 2) / resolution
        
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                # Local Cartesian coordinates (km from center position)
                # This ensures equal area coverage - each step is the same surface distance
                local_x = -radius_km + i * step_km
                local_y = -radius_km + j * step_km
                
                # Convert local Cartesian to lat/lon using spherical geometry
                lat, lon = self._local_cartesian_to_latlon(local_x, local_y, center_lat, center_lon)
                
                # Clamp latitude to valid range (this is the only place we should need clamping)
                lat = max(-89.99, min(89.99, lat))
                
                # Handle longitude wrapping
                while lon < -180:
                    lon += 360
                while lon > 180:
                    lon -= 360
                
                # Get elevation and color
                elevation = self.heightmap.height_at(lat, lon)
                color = self._sample_world_map_color_corrected(lat, lon)
                
                # Convert back to 3D world coordinates for rendering (using local coords)
                x = local_x * self.scale_horizontal / 1000.0  # Convert km to scaled units
                y = local_y * self.scale_horizontal / 1000.0
                z = (elevation - camera_altitude) * self.scale_vertical
                
                position = Vector3(x, y, z)
                normal = self._calculate_vertex_normal(lat, lon, step_km / earth_radius_km)  # Use angular step size
                
                # Determine vertex type and create appropriate vertex
                if elevation > self.sea_level:
                    # Land vertex
                    vertices[(i, j)] = TerrainVertex(position, normal, color, lat, lon)
                else:
                    # Sea vertex - create at sea surface
                    z_sea = (self.sea_surface_elevation - camera_altitude) * self.scale_vertical
                    position_sea = Vector3(x, y, z_sea)
                    normal_sea = Vector3(0, 0, 1)
                    sea_color = self._get_sea_color(color, elevation)
                    vertices[(i, j)] = TerrainVertex(position_sea, normal_sea, sea_color, lat, lon)
        
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
                
                # Update triangle colors based on centroid sampling for better coastline rendering
                self._update_triangle_color_from_centroid(triangle1, center_lat, center_lon)
                self._update_triangle_color_from_centroid(triangle2, center_lat, center_lon)
                
                # Determine if triangles are primarily land or sea based on vertex elevations
                # Use the vertices we already have - they contain the elevation data
                quad_elevations = [
                    self.heightmap.height_at(v1.lat, v1.lon),
                    self.heightmap.height_at(v2.lat, v2.lon), 
                    self.heightmap.height_at(v3.lat, v3.lon),
                    self.heightmap.height_at(v4.lat, v4.lon)
                ]
                
                # Use majority rule for triangle classification
                land_count = sum(1 for elev in quad_elevations if elev > self.sea_level)
                
                if land_count >= 2:  # Majority land
                    land_triangles.extend([triangle1, triangle2])
                else:  # Majority sea
                    sea_triangles.extend([triangle1, triangle2])
    
    def _update_triangle_color_from_centroid(self, triangle, center_lat, center_lon):
        """
        Update all vertices in a triangle to use the color sampled from the triangle's centroid.
        This provides more consistent colors across triangles, especially for coastlines.
        """
        # Calculate triangle centroid in geographic coordinates
        total_lat = triangle.v1.lat + triangle.v2.lat + triangle.v3.lat
        total_lon = triangle.v1.lon + triangle.v2.lon + triangle.v3.lon
        centroid_lat = total_lat / 3.0
        centroid_lon = total_lon / 3.0
        
        # Sample color at the centroid
        centroid_color = self._sample_world_map_color_corrected(centroid_lat, centroid_lon)
        
        # Apply this color to all vertices in the triangle
        triangle.v1.color = centroid_color
        triangle.v2.color = centroid_color
        triangle.v3.color = centroid_color
    
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
        # Sample heights at surrounding points with polar clamping
        h_center = self.heightmap.height_at(lat, lon)
        
        # Clamp latitude sampling to valid range to handle poles
        lat_north = min(89.9, lat + sample_distance)
        lat_south = max(-89.9, lat - sample_distance)
        
        h_north = self.heightmap.height_at(lat_north, lon)
        h_south = self.heightmap.height_at(lat_south, lon)
        h_east = self.heightmap.height_at(lat, lon + sample_distance)
        h_west = self.heightmap.height_at(lat, lon - sample_distance)
        
        # Calculate gradient vectors using actual sample distances
        actual_lat_distance = lat_north - lat_south
        dx = (h_east - h_west) / (2 * sample_distance * self.scale_horizontal)
        dy = (h_north - h_south) / (actual_lat_distance * self.scale_horizontal)
        
        # Normal vector from cross product of tangent vectors
        tangent_x = Vector3(1, 0, dx * self.scale_vertical)
        tangent_y = Vector3(0, 1, dy * self.scale_vertical)
        normal = tangent_x.cross(tangent_y).normalize()
        
        return normal
    
    def render_to_surface(self, surface: pygame.Surface, camera: Camera3D, 
                         viewport_x: int, viewport_y: int, viewport_w: int, viewport_h: int):
        """Render multi-tier LOD terrain mesh to pygame surface with proper layering"""
        if not self._has_any_triangles():
            return
        
        # Increment debug frame counter for limiting debug output
        self.debug_frame_counter = (self.debug_frame_counter + 1) % 60  # Reset every 60 frames
        self.sky_fill_events_this_frame = 0  # Reset sky-fill event counter
        self.large_triangles_this_frame = 0  # Reset large triangle counter
        
        # Periodically clear logged triangles to catch new edge cases
        if self.debug_frame_counter == 0:
            self.logged_large_triangles.clear()
        
        # Combine all triangles with distance and layer information
        all_triangles = []
        
        # Add sun triangles first - render as background (sky layer)
        for triangle in self.sun_triangles:
            # Use negative distance to ensure sun renders as background (first)
            distance = -999999999.0  # Negative distance for background rendering
            all_triangles.append((triangle, 'sun', 'sun', distance))
        
        # Add all LOD levels - render back to front by distance
        # Horizon level (furthest)
        for triangle in self.horizon_sea_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'sea', 'horizon', distance))
        
        for triangle in self.horizon_land_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'land', 'horizon', distance))
        
        # Outer level 
        for triangle in self.outer_sea_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'sea', 'outer', distance))
        
        for triangle in self.outer_land_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'land', 'outer', distance))
        
        # Mid level
        for triangle in self.mid_sea_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'sea', 'mid', distance))
        
        for triangle in self.mid_land_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'land', 'mid', distance))
        
        # Inner level
        for triangle in self.inner_sea_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'sea', 'inner', distance))
        
        for triangle in self.inner_land_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'land', 'inner', distance))
        
        # Ultra level (closest, highest detail)
        for triangle in self.ultra_sea_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'sea', 'ultra', distance))
        
        for triangle in self.ultra_land_triangles:
            distance = camera.get_distance_to(triangle.center)
            all_triangles.append((triangle, 'land', 'ultra', distance))
        
        # Sort by layer priority FIRST, then by distance within each layer
        # Higher detail layers render LAST (on top) - reverse order for proper layering
        # Layer priority: sun < horizon < outer < mid < inner < ultra (ultra renders last/on top)
        layer_priority = {'sun': 0, 'horizon': 1, 'outer': 2, 'mid': 3, 'inner': 4, 'ultra': 5}
        sorted_triangles = sorted(all_triangles, 
                                key=lambda t: (layer_priority.get(t[2], 0), -t[3]),  # Layer priority FIRST, then reverse distance (closer last)
                                reverse=False)  # Sort ascending so ultra (5) renders last
        
        # Create clipping rectangle for viewport
        clip_rect = pygame.Rect(viewport_x, viewport_y, viewport_w, viewport_h)
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        
        try:
            # Calculate minimum no-cull distance based on triangle spacing
            # Ultra mesh: 1.0° radius / 28 resolution = 0.036° per triangle  
            # At scale_horizontal = 13050: triangle_edge ≈ 0.036° × 13050 = ~470 units
            # 3 triangle distances = ~1410 units for safe close-range rendering
            min_no_cull_distance = 8000.0  # Never cull triangles closer than this (very conservative)
            
            # Render each triangle with proper layer priority and distance culling only
            for triangle, triangle_type, layer, distance in sorted_triangles:
                # Ultra LOD gets absolute protection - never cull for landing safety
                if layer == 'ultra':
                    # Ultra LOD triangles always render - critical for landing and close terrain
                    pass  # Skip all culling checks
                elif triangle_type == 'sun':
                    max_distance = 5000000.0  # Sun triangles at astronomical distances
                elif distance <= min_no_cull_distance:
                    # Always render close triangles regardless of frustum culling (for landing safety)
                    pass  # No distance culling for very close triangles
                else:
                    # Layer-specific maximum distance culling for performance only
                    if layer == 'horizon':
                        max_distance = 200000.0  # ~200km for horizon visibility
                    elif layer == 'outer':  
                        max_distance = 120000.0  # ~120km for distant terrain
                    elif layer == 'mid':
                        max_distance = 50000.0   # ~50km for mid-range
                    elif layer == 'inner':
                        max_distance = 20000.0   # ~20km for detailed terrain
                    else:
                        max_distance = 100000.0  # Default fallback
                    
                    # Skip triangle if beyond maximum distance for this LOD level
                    if distance > max_distance:
                        continue
                
                self._render_triangle(surface, triangle, camera, viewport_x, viewport_y, 
                                    viewport_w, viewport_h, triangle_type, layer, distance)
        finally:
            # Restore original clipping
            surface.set_clip(old_clip)
            
            # Debug summary for sky-filling events
            if DEBUG_SKY_FILLING and self.sky_fill_events_this_frame > 3:
                print(f"SKY-FILL SUMMARY: {self.sky_fill_events_this_frame} triangles blocked this frame")
    
    def _has_any_triangles(self) -> bool:
        """Check if any triangles exist in any LOD level or sun"""
        return (len(self.ultra_land_triangles) > 0 or len(self.ultra_sea_triangles) > 0 or
                len(self.inner_land_triangles) > 0 or len(self.inner_sea_triangles) > 0 or
                len(self.mid_land_triangles) > 0 or len(self.mid_sea_triangles) > 0 or
                len(self.outer_land_triangles) > 0 or len(self.outer_sea_triangles) > 0 or
                len(self.horizon_land_triangles) > 0 or len(self.horizon_sea_triangles) > 0 or
                len(self.sun_triangles) > 0)
    
    def _render_triangle(self, surface: pygame.Surface, triangle: TerrainTriangle, camera: Camera3D,
                        viewport_x: int, viewport_y: int, viewport_w: int, viewport_h: int, 
                        triangle_type: str = 'land', layer: str = 'inner', distance: float = 0.0):
        """Render a single triangle to the surface with layer and type-specific lighting"""
        
        # First, check if triangle needs near-plane clipping
        clipped_triangles = camera.clip_triangle_near_plane([triangle.v1, triangle.v2, triangle.v3])
        
        # If triangle is completely clipped by near plane, skip rendering
        if not clipped_triangles:
            return
        
        # For now, only render the first clipped triangle (proper clipping would handle multiple)
        # This prevents projection instability without complex geometry processing
        
        # Ultra LOD gets absolute protection from all culling for landing safety
        if layer == 'ultra':
            is_ultra_lod = True
            is_close_triangle = True  # Treat all ultra triangles as close
        else:
            is_ultra_lod = False
            # Calculate if this is a close triangle that should avoid aggressive culling
            min_no_cull_distance = 8000.0  # Increased from 5000 for more permissive close triangle handling
            is_close_triangle = distance <= min_no_cull_distance
        
        # Project vertices to screen coordinates with permissive culling
        screen_coords = []
        valid_coords = []
        
        for vertex in [triangle.v1, triangle.v2, triangle.v3]:
            # For ultra LOD triangles, bypass ALL culling in project_to_2d and force projection
            if is_ultra_lod:
                # Ultra LOD gets forced projection - calculate screen coordinates directly
                relative_pos = vertex.position - camera.position
                x_cam = relative_pos.dot(camera.right)
                y_cam = relative_pos.dot(camera.up)
                z_cam = relative_pos.dot(camera.forward)
                
                # Use safe z_cam for projection
                z_cam_safe = max(z_cam, 0.1)
                
                # Direct projection without any culling
                fov_rad = math.radians(60.0)  # Default FOV
                tan_half_fov = math.tan(fov_rad / 2)
                aspect_ratio = viewport_w / viewport_h
                
                x_ndc = x_cam / (z_cam_safe * tan_half_fov * aspect_ratio)
                y_ndc = y_cam / (z_cam_safe * tan_half_fov)
                
                screen_x = int((x_ndc + 1) * viewport_w / 2)
                screen_y = int((1 - y_ndc) * viewport_h / 2)
                
                # Force coordinates for ultra LOD - no culling at all
                coord = (screen_x + viewport_x, screen_y + viewport_y)
                screen_coords.append(coord)
                valid_coords.append(coord)
            else:
                # Normal projection with culling for other LOD levels
                screen_pos = camera.project_to_2d(vertex.position, viewport_w, viewport_h)
                if screen_pos is not None:
                    # Offset by viewport position
                    coord = (screen_pos[0] + viewport_x, screen_pos[1] + viewport_y)
                    screen_coords.append(coord)
                    valid_coords.append(coord)
                else:
                    screen_coords.append(None)
        
        # Render triangle if ANY vertex is visible OR if close to camera OR if ultra LOD
        # This prevents triangle pop-in/pop-out during camera movement
        if len(valid_coords) == 0 and not is_close_triangle and not is_ultra_lod:
            # Debug: Check if this is a near-triangle culling issue
            if DEBUG_CULLING and distance < 20000:  # Only debug relatively close triangles
                # Check if any vertex is actually in frustum
                vertices_in_frustum = 0
                for vertex in [triangle.v1, triangle.v2, triangle.v3]:
                    relative_pos = vertex.position - camera.position
                    z_cam = relative_pos.dot(camera.forward)
                    if z_cam > 1.0:  # In front of camera
                        # Calculate frustum bounds
                        x_cam = relative_pos.dot(camera.right)
                        y_cam = relative_pos.dot(camera.up)
                        fov_rad = math.radians(60.0)
                        tan_half_fov = math.tan(fov_rad / 2)
                        aspect_ratio = viewport_w / viewport_h
                        
                        # Check if within frustum
                        x_bound = z_cam * tan_half_fov * aspect_ratio
                        y_bound = z_cam * tan_half_fov
                        if abs(x_cam) <= x_bound and abs(y_cam) <= y_bound:
                            vertices_in_frustum += 1
                
                if vertices_in_frustum > 0:
                    print(f"CULL ERROR: Near triangle at dist={distance:.0f} layer={layer} has {vertices_in_frustum} vertices in frustum but was culled")
            
            # No vertices visible, not close, and not ultra LOD - can skip
            return
        
        # Handle partial triangles - remove coordinate substitution that caused tent effect
        final_coords = []
        for i, coord in enumerate(screen_coords):
            if coord is not None:
                final_coords.append(coord)
        
        # Only render triangles with enough valid coordinates
        # Allow partial triangles for ALL LOD levels to enable proper edge clipping
        if len(final_coords) < 1:
            # Need at least 1 valid vertex to render any triangle
            return
        
        # For triangles with fewer than 3 vertices, we'll handle them as partial triangles
        # Remove the exact-3-coordinate requirement to allow edge clipping
        
        # Calculate triangle color with consistent lighting across all LOD levels
        if triangle_type == 'sun':
            # Sun triangles - no lighting, use vertex color directly
            avg_color = (
                (triangle.v1.color[0] + triangle.v2.color[0] + triangle.v3.color[0]) // 3,
                (triangle.v1.color[1] + triangle.v2.color[1] + triangle.v3.color[1]) // 3,
                (triangle.v1.color[2] + triangle.v2.color[2] + triangle.v3.color[2]) // 3
            )
            final_color = avg_color
            
        elif triangle_type == 'sea':
            # Sea surface lighting - consistent across all LOD levels
            light_direction = Vector3(0.2, 0.3, 0.9).normalize()
            light_intensity = max(0.7, 0.85 + 0.15 * triangle.normal.dot(light_direction))
            
            # Add slight shimmer effect for water
            shimmer = 0.05 * math.sin(triangle.center.x * 0.0005 + triangle.center.y * 0.0005)
            light_intensity = min(1.0, light_intensity + shimmer)
            
            # Use average color of vertices
            avg_color = (
                (triangle.v1.color[0] + triangle.v2.color[0] + triangle.v3.color[0]) // 3,
                (triangle.v1.color[1] + triangle.v2.color[1] + triangle.v3.color[1]) // 3,
                (triangle.v1.color[2] + triangle.v2.color[2] + triangle.v3.color[2]) // 3
            )
            
            # Apply consistent atmospheric haze only for horizon layer
            if layer == 'horizon':
                haze_factor = 0.15  # Reduced haze
                haze_color = (160, 180, 200)
                avg_color = (
                    int(avg_color[0] * (1 - haze_factor) + haze_color[0] * haze_factor),
                    int(avg_color[1] * (1 - haze_factor) + haze_color[1] * haze_factor),
                    int(avg_color[2] * (1 - haze_factor) + haze_color[2] * haze_factor)
                )
                light_intensity = 0.7 + (light_intensity - 0.7) * 0.8
            
            # Apply lighting
            final_color = (
                int(avg_color[0] * light_intensity),
                int(avg_color[1] * light_intensity),
                int(avg_color[2] * light_intensity)
            )
            
        else:
            # Land lighting - consistent across all LOD levels
            light_direction = Vector3(0.5, 0.3, 0.8).normalize()
            light_intensity = max(0.5, triangle.normal.dot(light_direction))  # Consistent base lighting
            
            # Use average color of vertices
            avg_color = (
                (triangle.v1.color[0] + triangle.v2.color[0] + triangle.v3.color[0]) // 3,
                (triangle.v1.color[1] + triangle.v2.color[1] + triangle.v3.color[1]) // 3,
                (triangle.v1.color[2] + triangle.v2.color[2] + triangle.v3.color[2]) // 3
            )
            
            # Apply consistent atmospheric haze only for horizon layer
            if layer == 'horizon':
                haze_factor = 0.15  # Reduced haze
                haze_color = (160, 180, 200)
                avg_color = (
                    int(avg_color[0] * (1 - haze_factor) + haze_color[0] * haze_factor),
                    int(avg_color[1] * (1 - haze_factor) + haze_color[1] * haze_factor),
                    int(avg_color[2] * (1 - haze_factor) + haze_color[2] * haze_factor)
                )
                light_intensity = 0.7 + (light_intensity - 0.7) * 0.8
            
            # Apply lighting
            final_color = (
                int(avg_color[0] * light_intensity),
                int(avg_color[1] * light_intensity),
                int(avg_color[2] * light_intensity)
            )
        
        # Draw filled triangle/polygon with support for partial triangles
        if len(final_coords) >= 3:
            # Full triangle - use normal polygon drawing
            # Basic coordinate validation to prevent extreme rendering issues
            # Use moderately permissive validation - balance between edge cases and extreme projections
            valid_triangle = True
            extreme_coords = []
            for coord in final_coords:
                if abs(coord[0]) > 75000 or abs(coord[1]) > 75000:  # 1.5x more permissive than original
                    valid_triangle = False
                    extreme_coords.append(coord)
            
            if valid_triangle:
                # Track rare edge cases - look for triangles that pass validation but are still large
                if TRACK_EDGE_CASES and len(final_coords) >= 3:
                    max_coord = max(max(abs(c[0]), abs(c[1])) for c in final_coords)
                    if max_coord > 50000:  # Large but still valid triangles
                        # Create a unique key for this triangle to avoid spam
                        triangle_key = tuple(sorted(final_coords[:3]))
                        if triangle_key not in self.logged_large_triangles:
                            self.large_triangles_this_frame += 1
                            if self.large_triangles_this_frame <= 2:  # Log first 2 unique per frame
                                triangle_area = self._calculate_triangle_area(final_coords)
                                print(f"LARGE TRIANGLE: coords={final_coords[:3]} max_coord={max_coord} area={triangle_area}")
                                self.logged_large_triangles.add(triangle_key)
                
                pygame.draw.polygon(surface, final_color, final_coords)
            elif DEBUG_SKY_FILLING:
                # Count sky-filling events but only log first few per frame
                self.sky_fill_events_this_frame += 1
                if self.sky_fill_events_this_frame <= 3:  # Only log first 3 per frame
                    max_coord = max(max(abs(c[0]), abs(c[1])) for c in extreme_coords) if extreme_coords else 0
                    print(f"SKY-FILL BLOCKED: Triangle at {triangle.center.x:.1f},{triangle.center.y:.1f} max_coord={max_coord}")
        elif len(final_coords) == 2:
            # Partial triangle with 2 vertices - draw as a thick line
            valid_line = True
            extreme_coords = []
            for coord in final_coords:
                if abs(coord[0]) > 75000 or abs(coord[1]) > 75000:  # 1.5x more permissive than original
                    valid_line = False
                    extreme_coords.append(coord)
            
            if valid_line:
                pygame.draw.line(surface, final_color, final_coords[0], final_coords[1], 2)
            elif DEBUG_SKY_FILLING and self.sky_fill_events_this_frame <= 3:
                self.sky_fill_events_this_frame += 1
                print(f"SKY-FILL BLOCKED: Line at {triangle.center.x:.1f},{triangle.center.y:.1f}")
        elif len(final_coords) == 1:
            # Partial triangle with 1 vertex - draw as a small circle/point
            coord = final_coords[0]
            if abs(coord[0]) <= 75000 and abs(coord[1]) <= 75000:  # 1.5x more permissive than original
                pygame.draw.circle(surface, final_color, coord, 1)
            elif DEBUG_SKY_FILLING and self.sky_fill_events_this_frame <= 3:
                self.sky_fill_events_this_frame += 1
                print(f"SKY-FILL BLOCKED: Point at {triangle.center.x:.1f},{triangle.center.y:.1f} coord={abs(coord[0])},{abs(coord[1])}")
        
        # Show debug summary every 60 frames
        if TRACK_EDGE_CASES and self.debug_frame_counter == 0:
            total_large = len(self.logged_large_triangles)
            if total_large > 0:
                print(f"🔍 EDGE CASE SUMMARY: {total_large} unique large triangles detected in last 60 frames")
    
    def _calculate_triangle_area(self, coords):
        """Calculate the area of a triangle given three screen coordinates"""
        if len(coords) < 3:
            return 0
        x1, y1 = coords[0]
        x2, y2 = coords[1]
        x3, y3 = coords[2]
        return abs((x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)) / 2)
    
    def get_terrain_height_at_camera(self, lat: float, lon: float) -> float:
        """Get terrain height at camera position for ground level reference"""
        return self.heightmap.height_at(lat, lon) * self.scale_vertical
    
    def get_mesh_statistics(self) -> Dict[str, Any]:
        """Get statistics about the current multi-tier LOD mesh for debugging"""
        return {
            "ultra_land_triangles": len(self.ultra_land_triangles),
            "ultra_sea_triangles": len(self.ultra_sea_triangles),
            "inner_land_triangles": len(self.inner_land_triangles),
            "inner_sea_triangles": len(self.inner_sea_triangles),
            "mid_land_triangles": len(self.mid_land_triangles),
            "mid_sea_triangles": len(self.mid_sea_triangles),
            "outer_land_triangles": len(self.outer_land_triangles),
            "outer_sea_triangles": len(self.outer_sea_triangles),
            "horizon_land_triangles": len(self.horizon_land_triangles),
            "horizon_sea_triangles": len(self.horizon_sea_triangles),
            "sun_triangles": len(self.sun_triangles),
            "land_triangles": (len(self.ultra_land_triangles) + len(self.inner_land_triangles) + 
                              len(self.mid_land_triangles) + len(self.outer_land_triangles) + 
                              len(self.horizon_land_triangles)),
            "sea_triangles": (len(self.ultra_sea_triangles) + len(self.inner_sea_triangles) + 
                             len(self.mid_sea_triangles) + len(self.outer_sea_triangles) + 
                             len(self.horizon_sea_triangles)),
            "total_triangles": (len(self.ultra_land_triangles) + len(self.ultra_sea_triangles) +
                               len(self.inner_land_triangles) + len(self.inner_sea_triangles) + 
                               len(self.mid_land_triangles) + len(self.mid_sea_triangles) +
                               len(self.outer_land_triangles) + len(self.outer_sea_triangles) +
                               len(self.horizon_land_triangles) + len(self.horizon_sea_triangles) +
                               len(self.sun_triangles)),
            "ultra_total": len(self.ultra_land_triangles) + len(self.ultra_sea_triangles),
            "inner_total": len(self.inner_land_triangles) + len(self.inner_sea_triangles),
            "mid_total": len(self.mid_land_triangles) + len(self.mid_sea_triangles),
            "outer_total": len(self.outer_land_triangles) + len(self.outer_sea_triangles),
            "horizon_total": len(self.horizon_land_triangles) + len(self.horizon_sea_triangles),
            "mesh_resolution": self.inner_mesh_resolution,  # For compatibility with old code
            "ultra_mesh_resolution": self.ultra_mesh_resolution,
            "inner_mesh_resolution": self.inner_mesh_resolution,
            "mid_mesh_resolution": self.mid_mesh_resolution,
            "outer_mesh_resolution": self.outer_mesh_resolution,
            "horizon_mesh_resolution": self.horizon_mesh_resolution,
            "ultra_radius_deg": self.ultra_radius_deg,
            "inner_radius_deg": self.inner_radius_deg,
            "mid_radius_deg": self.mid_radius_deg,
            "outer_radius_deg": self.outer_radius_deg,
            "horizon_radius_deg": self.horizon_radius_deg,
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
    
    # Camera position (airship position + eye level height above deck)
    eye_level_height = 1.8  # 6 feet above deck in meters
    camera_pos = Vector3(0, 0, eye_level_height)  # Camera at eye level above airship position
    
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


def _azimuth_to_compass_direction(azimuth: float) -> str:
    """Convert azimuth angle to compass direction string"""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                 "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = int((azimuth + 11.25) / 22.5) % 16
    return directions[index]