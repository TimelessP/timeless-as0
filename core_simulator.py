"""
Core Simulator for Airship Zero
Centralized game state management and physics simulation
"""
import json
import time
import math
import os
import uuid
import site
import random
from theme import CRATE_TYPE_COLORS
import platform
from pathlib import Path
import sys
from typing import Dict, Any, Optional, Tuple, List

# Cargo grid pixel size (must match scene_cargo.GRID_SIZE)
CARGO_GRID_PX = 8


def get_assets_path(subdir: str = "") -> str:
    """
    Get the correct path to assets directory, whether running from source or installed package.
    
    Args:
        subdir: Subdirectory within assets (e.g., "books", "fonts", "png")
    
    Returns:
        Path to the assets directory or subdirectory
    """
    # Try multiple possible locations for assets
    possible_locations = [
        # Development/source directory (relative to this file)
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"),
        # Current working directory
        os.path.join(os.getcwd(), "assets"),
        # Package installation directory (same directory as this file)
        os.path.join(os.path.dirname(__file__), "assets"),
    ]
    
    # Try to find Python package installation paths
    try:
        # Check site-packages directories
        for site_dir in site.getsitepackages():
            possible_locations.append(os.path.join(site_dir, "assets"))
            possible_locations.append(os.path.join(site_dir, "airshipzero", "assets"))
        
        # Check user site directory
        user_site = site.getusersitepackages()
        if user_site:
            possible_locations.append(os.path.join(user_site, "assets"))
            possible_locations.append(os.path.join(user_site, "airshipzero", "assets"))
    except:
        pass
    
    # For uv tool installs, check relative to Python executable
    try:
        exe_dir = os.path.dirname(sys.executable)
        possible_locations.append(os.path.join(exe_dir, "assets"))
        # uv might install in a lib subdirectory
        possible_locations.append(os.path.join(exe_dir, "lib", "assets"))
    except:
        pass
    
    # Check each possible location
    for base_path in possible_locations:
        if subdir:
            full_path = os.path.join(base_path, subdir)
        else:
            full_path = base_path
            
        if os.path.exists(full_path):
            return full_path
    
    # Fallback to relative path
    if subdir:
        return os.path.join("assets", subdir)
    else:
        return "assets"


class CoreSimulator:
    def _get_user_books_dir(self) -> Path:
        """Return the path to the user's custom books directory, cross-platform."""
        if sys.platform == "win32":
            home = os.environ.get("USERPROFILE")
            docs = os.path.join(home, "Documents") if home else None
        elif sys.platform == "darwin":
            home = os.environ.get("HOME")
            docs = os.path.join(home, "Documents") if home else None
        else:
            home = os.environ.get("HOME")
            docs = os.path.join(home, "Documents") if home else None
        if docs:
            return Path(docs) / "AirshipZero" / "books"
        return None

    def _scan_user_books(self) -> list:
        """Scan the user books directory and return a list of book ref dicts."""
        user_books_dir = self._get_user_books_dir()
        books = []
        if user_books_dir and user_books_dir.is_dir():
            for fname in sorted(os.listdir(user_books_dir)):
                if fname.endswith(".md") and (user_books_dir / fname).is_file():
                    title = fname[:-3].replace('-', ' ').replace('_', ' ').title()
                    books.append({
                        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"user:{fname}")),
                        "type": "user",
                        "title": title,
                        "source": str(user_books_dir / fname)
                    })
        return books

    def _scan_in_game_books(self) -> list:
        """Scan the assets/books directory for in-game books."""
        books_dir = Path(get_assets_path("books"))
        books = []
        if books_dir.is_dir():
            for fname in sorted(os.listdir(books_dir)):
                if fname.endswith(".md") and (books_dir / fname).is_file():
                    title = fname[:-3].replace('-', ' ').replace('_', ' ').title()
                    books.append({
                        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"in_game:{fname}")),
                        "type": "in_game",
                        "title": title,
                        "source": str(books_dir / fname)
                    })
        return books

    def refresh_library_books(self):
        """Refresh the library book list, merging user and in-game books, preserving order where possible."""
        state = self.game_state["library"]
        # Always reload user books from disk
        user_books = self._scan_user_books()
        user_book_ids = {b["id"] for b in user_books}
        # Only keep user books that still exist
        order = [b for b in state.get("order", []) if not (b["type"] == "user" and b["id"] not in user_book_ids)]
        # Add new user books to the end
        known_user_ids = {b["id"] for b in order if b["type"] == "user"}
        for ub in user_books:
            if ub["id"] not in known_user_ids:
                order.append(ub)
        # In-game books: only those present in in_game_books list
        in_game_books = self._scan_in_game_books()
        in_game_book_ids = {b["id"] for b in in_game_books}
        present_in_game_ids = set(b["id"] for b in state.get("in_game_books", []))
        order = [b for b in order if not (b["type"] == "in_game" and b["id"] not in present_in_game_ids)]
        # Add any new in-game books present in library but not in order (as full book dicts)
        known_in_game_ids = {b["id"] for b in order if b["type"] == "in_game"}
        for ib in state.get("in_game_books", []):
            if ib["id"] not in known_in_game_ids:
                order.append(dict(ib))
        # Ensure all in_game_books are present in order (fix for empty order)
        order_ids = {b["id"] for b in order}
        for ib in state.get("in_game_books", []):
            if ib["id"] not in order_ids:
                order.append(dict(ib))
        state["order"] = order
        print(f"[DEBUG] refresh_library_books: final order has {len(order)} books: {[b.get('title') for b in order]}")

    def get_library_books(self) -> list:
        """Return the current ordered list of book refs for the library scene."""
        print("[DEBUG] get_library_books called")
        self.refresh_library_books()
        books = list(self.game_state["library"]["order"])
        print(f"[DEBUG] get_library_books returning {len(books)} books")
        return books

    def add_in_game_book_to_library(self, book_id: str):
        """Add an in-game book to the library (by id)."""
        in_game_books = self._scan_in_game_books()
        book = next((b for b in in_game_books if b["id"] == book_id), None)
        print(f"[DEBUG] add_in_game_book_to_library: book_id={book_id} found={book is not None}")
        if book:
            state = self.game_state["library"]
            in_game_ids = {b["id"] for b in state.get("in_game_books", [])}
            order_ids = {b["id"] for b in state.get("order", [])}
            if book["id"] not in in_game_ids:
                print(f"[DEBUG] Adding book {book['id']} to in_game_books")
                state.setdefault("in_game_books", []).append(book)
            else:
                print(f"[DEBUG] Book {book['id']} already in in_game_books")
            # Ensure book is also in the order list
            if book["id"] not in order_ids:
                print(f"[DEBUG] Adding book {book['id']} to order list")
                state.setdefault("order", []).append(book)
            self.refresh_library_books()

    def remove_in_game_book_from_library(self, book_id: str):
        """Remove an in-game book from the library (by id), e.g. when moved to cargo hold."""
        state = self.game_state["library"]
        print(f"[DEBUG] refresh_library_books: in_game_books={len(state.get('in_game_books', []))} order={len(state.get('order', []))}")
        state["in_game_books"] = [b for b in state.get("in_game_books", []) if b["id"] != book_id]
        self.refresh_library_books()

    def get_book_by_id(self, book_id: str):
        """Get a book ref by id from the current library list."""
        for b in self.get_library_books():
            if b["id"] == book_id:
                return b
        return None

    def set_library_order(self, new_order: list):
        """Set the library order by list of book ids."""
        books_by_id = {b["id"]: b for b in self.get_library_books()}
        self.game_state["library"]["order"] = [books_by_id[bid] for bid in new_order if bid in books_by_id]

    # Save/load logic: only persist in_game_books and order (user books are always loaded from disk)
    """
    Centralized simulator core that manages all game state and physics.
    All scenes reference this single source of truth.
    """
    
    def __init__(self, custom_save_path: Optional[str] = None):
        self.game_state = self._create_initial_game_state()
        self.last_update_time = time.time()
        self.total_sim_time = 0.0
        self.running = False
        
        # Store custom save path if provided
        self.custom_save_path = Path(custom_save_path) if custom_save_path else None
        
    def _get_app_data_dir(self) -> Path:
        """Get the application data directory for the current OS"""
        app_name = "AirshipZero"
        
        system = platform.system()
        
        if system == "Windows":
            # Windows: %APPDATA%\AirshipZero
            base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
            app_dir = Path(base_dir) / app_name
        elif system == "Darwin":  # macOS
            # macOS: ~/Library/Application Support/AirshipZero
            app_dir = Path.home() / "Library" / "Application Support" / app_name
        else:  # Linux and other Unix-like systems
            # Linux: ~/.local/share/AirshipZero (XDG Base Directory)
            xdg_data_home = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
            app_dir = Path(xdg_data_home) / app_name
        
        # Create directory if it doesn't exist
        app_dir.mkdir(parents=True, exist_ok=True)
        
        return app_dir
    
    def _get_save_file_path(self, filename: str = "saved_game.json") -> Path:
        """Get the full path to the save file - custom path takes precedence over app data directory"""
        if self.custom_save_path:
            # If custom path provided, use it directly
            if self.custom_save_path.suffix:
                # Custom path includes filename
                return self.custom_save_path
            else:
                # Custom path is directory, append filename
                return self.custom_save_path / filename
        else:
            # Use default app data directory
            return self._get_app_data_dir() / filename
        
    def _create_initial_game_state(self) -> Dict[str, Any]:
        """Create the initial game state with all systems"""
        return {
            "gameInfo": {
                "version": "1.0.0",
                "created": time.time(),
                "lastSaved": time.time(),
                "totalFlightTime": 0.0,
                "sessionTime": 0.0,
                "paused": False
            },
            "settings": {
                "checkForUpdates": True,
                "lastUpdateCheck": 0.0,
                "updateCheckInterval": 86400.0,  # 24 hours in seconds
                "soundVolume": 0.5  # Sound effects volume (0.0 to 1.0)
            },
            "navigation": {
                "position": {
                    "latitude": 40.7128,  # NYC area
                    "longitude": -74.0060,
                    "altitude": 1250.0,
                    "heading": 45.0,
                    "track": 45.0
                },
                "motion": {
                    "indicatedAirspeed": 85.0,
                    "trueAirspeed": 88.2,
                    "groundSpeed": 82.5,
                    "verticalSpeed": 0.0,
                    "pitch": 0.0,
                    "roll": 0.0,
                    "yaw": 0.0,
                    "rateOfTurn": 0.0  # degrees per second
                },
                "controls": {
                    "rudder": 0.0,  # -30 to +30 degrees
                    "elevator": 0.0,  # -20 to +20 degrees
                    "ailerons": 0.0   # -25 to +25 degrees
                },
                "targets": {
                    "altitude": 1250.0,
                    "heading": 45.0,
                    "airspeed": 85.0
                },
                "mode": "manual",  # manual, heading_hold, altitude_hold, route_follow
                "autopilot": {
                    "engaged": False,
                    "headingHold": False,
                    "altitudeHold": False,
                    "airspeedHold": False,
                    "verticalSpeedHold": False,
                    "targetRudder": 0.0,  # Autopilot's target rudder position
                    "headingError": 0.0,  # Current heading error for autopilot
                    "turnRate": 0.0       # Autopilot's target turn rate
                },
                "route": {
                    "active": False,
                    "waypoints": [],
                    "currentWaypoint": 0,
                    "crossTrackError": 0.0
                },
                "mapView": {
                    "zoomLevel": 1.0,
                    "offsetX": 0.0,
                    "offsetY": 0.0
                }
            },
            "engine": {
                "running": True,
                "rpm": 2650.0,
                "targetRpm": 2650.0,
                "manifoldPressure": 24.5,
                "fuelFlow": 12.8,
                "oilPressure": 65.0,
                "oilTemperature": 185.0,
                "cylinderHeadTemp": 320.0,
                "exhaustGasTemp": 1450.0,
                "fuelPressure": 22.0,
                "controls": {
                    "throttle": 0.75,
                    "mixture": 0.85,
                    "propeller": 0.80
                },
                "propellerFeathered": False,
                "emergencyShutdown": False,
                "startupSequence": False
            },
            "electrical": {
                "batteryBusA": {
                    "switch": True,
                    "voltage": 12.6,
                    "current": 8.5,
                    "capacity": 24.0,  # Amp-hours
                    "remaining": 20.5
                },
                "batteryBusB": {
                    "switch": True,
                    "voltage": 12.5,
                    "current": 6.2,
                    "capacity": 24.0,
                    "remaining": 21.8
                },
                "alternator": {
                    "online": True,
                    "voltage": 14.2,
                    "current": 15.0,
                    "maxOutput": 60.0
                },
                "loads": {
                    "instruments": 3.2,
                    "navigation": 2.8,
                    "lighting": 4.5,
                    "radio": 1.8
                }
            },
            # Reworked fuel system: two tanks (forward & aft), each with transfer and dump pumps
            "fuel": {
                "totalCapacity": 360.0,  # 180 + 180
                "currentLevel": 280.0,
                "flowRate": 12.8,  # Current engine consumption GPH (informational)
                "engineFeedCut": False,  # True if no tank is feeding
                "tanks": {
                    "forward": {
                        "level": 140.0,
                        "capacity": 180.0,
                        "feed": True,          # Feeding engine
                        "transferRate": 0.0,   # 0..1 user slider -> transfers OUT to aft
                        "dumpRate": 0.0        # 0..1 user slider -> dumps overboard
                    },
                    "aft": {
                        "level": 140.0,
                        "capacity": 180.0,
                        "feed": True,          # Feeding engine
                        "transferRate": 0.0,   # OUT to forward
                        "dumpRate": 0.0
                    }
                }
            },
            "cargo": {
                "winch": {
                    "position": {"x": 160, "y": 50},
                    "cableLength": 0,
                    "attachedCrate": None,
                    "movementState": {"left": False, "right": False, "up": False, "down": False}
                },
                "cargoHold": [],
                "loadingBay": [],
                "totalWeight": 0.0,
                "centerOfGravity": {"x": 156.2, "y": 100.0},
                "maxCapacity": 500.0,
                "refreshAvailable": True,
                "crateTypes": {
                    "fuel_drum": {
                        "name": "Fuel Drum",
                        "dimensions": {"width": 4, "height": 6},
                        "contents": {"amount": 44, "unit": "gallons"},
                        "colors": CRATE_TYPE_COLORS.get("fuel_drum", {"outline": "#B97A56", "fill": "#8B5C2A"}),
                        "usable": True,
                        "useAction": "transfer_fuel",
                        "weight": 162.0  # kg (drum + fuel)
                    },
                    "books": {
                        "name": "Books",
                        "dimensions": {"width": 2, "height": 3},
                        "contents": {"amount": 1, "unit": "book"},
                        "colors": CRATE_TYPE_COLORS.get("books", {"outline": "#6B4F2B", "fill": "#C2B280"}),
                        "usable": True,
                        "useAction": "add_to_library",
                        "weight": 2.0
                    },
                    "medical_supplies": {
                        "name": "Medical Kit",
                        "dimensions": {"width": 4, "height": 3},
                        "contents": {"amount": 1, "unit": "kit"},
                        "colors": CRATE_TYPE_COLORS.get("medical_supplies", {"outline": "#A89C94", "fill": "#E5D8C0"}),
                        "usable": True,
                        "useAction": "add_medical_supplies",
                        "weight": 5.0
                    },
                    "food_rations": {
                        "name": "Food Rations",
                        "dimensions": {"width": 6, "height": 2},
                        "contents": {"amount": 7, "unit": "days"},
                        "colors": CRATE_TYPE_COLORS.get("food_rations", {"outline": "#7A6A4F", "fill": "#B7A16A"}),
                        "usable": True,
                        "useAction": "add_food",
                        "weight": 12.0
                    },
                    "spare_parts": {
                        "name": "Engine Parts",
                        "dimensions": {"width": 5, "height": 3},
                        "contents": {"amount": 1, "unit": "set"},
                        "colors": CRATE_TYPE_COLORS.get("spare_parts", {"outline": "#5C5C5C", "fill": "#A0A0A0"}),
                        "usable": False,
                        "weight": 15.0
                    },
                    "luxury_goods": {
                        "name": "Luxury Items",
                        "dimensions": {"width": 3, "height": 4},
                        "contents": {"amount": 1, "unit": "crate"},
                        "colors": CRATE_TYPE_COLORS.get("luxury_goods", {"outline": "#C2B280", "fill": "#E6D8AD"}),
                        "usable": False,
                        "weight": 3.0
                    }
                }
            },
            "environment": {
                "weather": {
                    "temperature": 15.0,  # Celsius
                    "pressure": 29.92,    # inHg
                    "humidity": 65.0,     # %
                    "visibility": 10.0,   # statute miles
                    "windSpeed": 8.0,     # knots
                    "windDirection": 270.0  # degrees
                },
                "time": {
                    "utc": time.time(),
                    "local": time.time(),
                    "timezone": "UTC",
                    "daylight": True
                }
            },
            "systems": {
                "warnings": [],
                "alerts": [],
                "failures": []
            },
            "library": {
                # List of book refs (dicts) in order, each with uuid4 id, type, title, source
                "order": [],
                # Only in-game books are tracked for presence; user books are always loaded from disk
                "in_game_books": [],  # List of book ref dicts for in-game books present in library
                "bookmarks": {}  # Dict mapping book id to page numbers
            }
        }
    
    def start_new_game(self):
        """Initialize a new game session"""
        self.game_state = self._create_initial_game_state()
        self.running = True
        self.last_update_time = time.time()
        self.total_sim_time = 0.0
        
    def pause_simulation(self):
        """Pause the simulation"""
        self.game_state["gameInfo"]["paused"] = True
        
    def resume_simulation(self):
        """Resume the simulation"""
        self.game_state["gameInfo"]["paused"] = False
        self.last_update_time = time.time()
        
    def save_game(self, filename: str = "saved_game.json") -> bool:
        """Save current game state to file - only persist in_game_books and order for library."""
        try:
            self.game_state["gameInfo"]["lastSaved"] = time.time()
            save_path = self._get_save_file_path(filename)
            if not self.custom_save_path or save_path.parent != Path('.'):
                save_path.parent.mkdir(parents=True, exist_ok=True)
            # Only save in_game_books and order for library
            state_copy = json.loads(json.dumps(self.game_state))
            lib = state_copy.get("library", {})
            # Remove user book refs from order before saving
            lib["order"] = [b for b in lib.get("order", []) if b.get("type") == "in_game"]
            # User books are always loaded from disk
            with open(save_path, 'w') as f:
                json.dump(state_copy, f, indent=2)
            print(f"✅ Game saved to {save_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to save game: {e}")
            return False
            
    def load_game(self, filename: str = "saved_game.json") -> bool:
        """Load game state from file in OS-appropriate app data directory"""
        try:
            save_path = self._get_save_file_path(filename)
            if not save_path.exists() or "books" not in self.game_state["library"]:
                print(f"⚠️ Save file not found: {save_path}")
                return False
            with open(save_path, 'r') as f:
                loaded_state = json.load(f)
            if "gameInfo" in loaded_state and "navigation" in loaded_state:
                # ...existing migration code...
                self.game_state = loaded_state
                # Ensure library section exists and is migrated
                lib = self.game_state.setdefault("library", {})
                if "order" not in lib and "books" in lib:
                    # Migrate old format: books list to order list only if 'books' exists
                    order = []
                    in_game_books = []
                    for fname in lib.get("books", []):
                        title = fname.replace('.md', '').replace('-', ' ').replace('_', ' ').title()
                        book_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"in_game:{fname}"))
                        ref = {"id": book_id, "type": "in_game", "title": title, "source": str(get_assets_path("books") + "/" + fname)}
                        order.append(ref)
                        in_game_books.append(ref)
                    lib["order"] = order
                    lib["in_game_books"] = in_game_books
                    lib.pop("books", None)
                if "in_game_books" not in lib:
                    # If missing, reconstruct from order
                    lib["in_game_books"] = [b for b in lib.get("order", []) if b.get("type") == "in_game"]
                # Do NOT remove user books from order; refresh_library_books will clean up missing ones
                self.running = True
                self.last_update_time = time.time()
                # ...existing cargo/winch migration code...
                print(f"✅ Game loaded from {save_path}")
                return True
            else:
                print(f"❌ Invalid save file format: {save_path}")
                return False
        except Exception as e:
            print(f"❌ Failed to load game: {e}")
            return False
            
    def has_saved_game(self, filename: str = "saved_game.json") -> bool:
        """Check if a saved game file exists in app data directory"""
        save_path = self._get_save_file_path(filename)
        return save_path.exists()
        
    def update(self, real_dt: float):
        """
        Update the simulation state
        real_dt: real-world time delta in seconds
        """
        if self.game_state["gameInfo"]["paused"] or not self.running:
            return
            
        # Simulation time step (could be scaled for faster/slower simulation)
        sim_dt = real_dt
        self.total_sim_time += sim_dt
        
        # Update game time
        self.game_state["gameInfo"]["sessionTime"] += sim_dt
        self.game_state["gameInfo"]["totalFlightTime"] += sim_dt
        
        # Update all systems
        self._update_fuel_system(sim_dt)
        self._update_engine(sim_dt)
        self._update_navigation(sim_dt)
        self._update_fuel_system(sim_dt)
        self._update_electrical_system(sim_dt)
        self._update_environment(sim_dt)
        self._update_systems_monitoring(sim_dt)
        self._update_cargo_system(sim_dt)
        
    def _update_engine(self, dt: float):
        """Update engine simulation"""
        engine = self.game_state["engine"]
        fuel = self.game_state["fuel"]
        
        if not engine["running"]:
            # Engine is off - RPM decays
            engine["rpm"] = max(0, engine["rpm"] - 500 * dt)
            engine["manifoldPressure"] = 14.7  # Atmospheric pressure
            engine["fuelFlow"] = 0.0
            engine["fuelPressure"] = 0.0
            return
            
        # Check fuel availability and pressure
        fuel_available = not fuel.get("engineFeedCut", False)
        total_fuel = fuel.get("currentLevel", 0.0)
        
        # Calculate fuel pressure based on fuel availability and tank levels
        if fuel_available and total_fuel > 0.1:
            # Normal fuel pressure when tanks are feeding
            base_fuel_pressure = 22.0
            # Reduce pressure if fuel is very low
            if total_fuel < 20.0:
                pressure_factor = total_fuel / 20.0  # Gradual pressure drop
                engine["fuelPressure"] = base_fuel_pressure * pressure_factor
            else:
                engine["fuelPressure"] = base_fuel_pressure
        else:
            # No fuel pressure when tanks not feeding or empty
            engine["fuelPressure"] = max(0.0, engine["fuelPressure"] - 50.0 * dt)
        
        # Engine is running - simulate performance based on fuel availability
        controls = engine["controls"]
        navigation = self.game_state["navigation"]
        altitude = navigation["position"]["altitude"]
        
        # Calculate mixture effectiveness based on altitude and mixture setting
        # Optimal mixture changes with altitude (leaner needed at higher altitudes)
        optimal_mixture_for_altitude = 0.85 - (altitude / 10000.0) * 0.15  # 0.85 at sea level, 0.70 at 10k ft
        optimal_mixture_for_altitude = max(0.50, min(0.95, optimal_mixture_for_altitude))
        
        # Calculate mixture power factor (bell curve around optimal)
        mixture_deviation = abs(controls["mixture"] - optimal_mixture_for_altitude)
        if mixture_deviation <= 0.05:  # Within 5% of optimal
            mixture_power_factor = 1.0
        elif mixture_deviation <= 0.15:  # Within 15% of optimal
            mixture_power_factor = 1.0 - (mixture_deviation - 0.05) * 2.0  # Linear falloff
        else:  # More than 15% off optimal
            mixture_power_factor = 0.8 - (mixture_deviation - 0.15) * 1.5  # Steeper falloff
        mixture_power_factor = max(0.3, mixture_power_factor)  # Minimum 30% power
        

        # Calculate atmospheric density factor for altitude effects
        # Standard atmosphere: sea level = 1.0, decreases with altitude
        altitude_density_factor = math.exp(-altitude / 29000.0)  # Roughly 50% at 20k ft
        
        # Calculate target RPM based on throttle, mixture, fuel availability, and altitude
        max_rpm = 2800.0
        
        # Prop pitch acts as a load: low pitch = low load, high pitch = high load
        # At low pitch, engine can reach max RPM; at high pitch, RPM may drop if engine can't overcome load
        # We'll model load as: load_factor = 0.5 + prop_pitch * 0.5 (0.5 at flat, 1.0 at max pitch)
        prop_pitch = controls["propeller"]
        base_load_factor = 0.5 + prop_pitch * 0.5
        
        # Altitude affects propeller load - thinner air reduces prop load
        # At high altitude, prop encounters less air resistance, so engine can spin faster
        altitude_load_reduction = 1.0 - (1.0 - altitude_density_factor) * 0.3  # Up to 30% load reduction
        load_factor = base_load_factor * altitude_load_reduction
        
        # Engine power also decreases with altitude due to less air density
        # Naturally aspirated engines lose about 3% power per 1000 ft
        engine_power_factor = altitude_density_factor
        
        # Base engine performance calculation
        base_target_rpm = controls["throttle"] * max_rpm * mixture_power_factor * engine_power_factor
        achievable_rpm = base_target_rpm / load_factor

        # Reduce achievable RPM if fuel pressure is low or fuel is cut
        fuel_factor = 1.0
        if engine["fuelPressure"] < 10.0:
            fuel_factor = engine["fuelPressure"] / 10.0  # Severe power loss below 10 PSI
        elif not fuel_available:
            fuel_factor = 0.0  # Complete power loss when fuel cut

        target_rpm = achievable_rpm * fuel_factor

        # RPM response (gradual change, faster decay when fuel-starved)
        rpm_diff = target_rpm - engine["rpm"]
        if fuel_factor < 1.0:
            # Faster RPM decay when fuel-starved
            rpm_rate = 5.0 if rpm_diff < 0 else 2.0
        else:
            # Slightly slower response at high load
            rpm_rate = 2.0 / load_factor
        engine["rpm"] += rpm_diff * rpm_rate * dt
        engine["rpm"] = max(0.0, engine["rpm"])  # Ensure non-negative RPM

        # Automatically shut down engine if RPM drops to zero
        if engine["rpm"] <= 0.0:
            engine["running"] = False
        
        # Manifold pressure correlates with throttle, altitude, and fuel availability
        # Atmospheric pressure decreases with altitude
        atmospheric_pressure = 29.92 * math.exp(-altitude / 29000.0)  # Rough altitude correction
        base_manifold = atmospheric_pressure + (controls["throttle"] * 15.0)
        engine["manifoldPressure"] = base_manifold * fuel_factor * mixture_power_factor
        
        # Fuel flow based on throttle, mixture, and actual engine performance
        if fuel_available and engine["fuelPressure"] > 5.0:
            # Base fuel flow scales with throttle and actual RPM
            base_flow = controls["throttle"] * 18.0  # Max ~18 GPH at full throttle
            
            # Mixture affects fuel flow directly - higher mixture = more fuel
            mixture_flow_factor = 0.6 + (controls["mixture"] * 0.8)  # 60-140% flow based on mixture
            
            # Reduce flow if fuel pressure is low
            pressure_factor = min(1.0, engine["fuelPressure"] / 22.0)
            
            # Also factor in actual RPM vs target (engine under stress uses more fuel)
            rpm_factor = engine["rpm"] / max(1.0, target_rpm) if target_rpm > 0 else 0.0
            
            engine["fuelFlow"] = base_flow * mixture_flow_factor * pressure_factor * rpm_factor
        else:
            # No fuel flow when fuel cut or very low pressure
            engine["fuelFlow"] = max(0.0, engine["fuelFlow"] - 25.0 * dt)
        
        # Temperature simulation (affected by fuel availability, engine load, and mixture)
        ambient_temp = self.game_state["environment"]["weather"]["temperature"]
        load_factor = controls["throttle"] * fuel_factor
        
        # Mixture significantly affects exhaust gas temperature
        # Lean mixture (low mixture setting) runs much hotter
        mixture_temp_factor = 2.0 - controls["mixture"]  # Lean = hot, Rich = cooler
        
        # Temperatures drop when engine is fuel-starved or not running properly
        if fuel_factor < 0.5 or engine["rpm"] < 1000:
            # Engine cooling down due to fuel starvation or low RPM
            target_oil_temp = ambient_temp + 50 + (load_factor * 40)
            target_cht = ambient_temp + 100 + (load_factor * 80)
            target_egt = 400 + (load_factor * 400)
        else:
            # Normal operating temperatures with mixture effects
            target_oil_temp = ambient_temp + 100 + (load_factor * 80)  # °F
            target_cht = ambient_temp + 180 + (load_factor * 140)     # °F
            # EGT strongly affected by mixture - lean mixtures run much hotter
            base_egt = 800 + (load_factor * 650)
            target_egt = base_egt * mixture_temp_factor
            target_egt = min(1800, target_egt)  # Cap at realistic maximum
        
        # Gradual temperature changes (faster cooling when fuel-starved)
        temp_rate = 15.0 * dt if fuel_factor < 0.5 else 10.0 * dt
        engine["oilTemperature"] += self._approach_value(
            engine["oilTemperature"], target_oil_temp, temp_rate
        )
        engine["cylinderHeadTemp"] += self._approach_value(
            engine["cylinderHeadTemp"], target_cht, temp_rate
        )
        engine["exhaustGasTemp"] += self._approach_value(
            engine["exhaustGasTemp"], target_egt, temp_rate * 2
        )
        
        # Oil pressure correlates with RPM and engine health
        base_oil_pressure = 20 + (engine["rpm"] / 2800.0) * 55
        # Reduce oil pressure if engine is struggling
        if fuel_factor < 0.8:
            oil_pressure_factor = 0.5 + (fuel_factor * 0.5)  # 50-100% oil pressure
            engine["oilPressure"] = base_oil_pressure * oil_pressure_factor
        else:
            engine["oilPressure"] = base_oil_pressure
        
    def _update_navigation(self, dt: float):
        """Update navigation and flight dynamics"""
        nav = self.game_state["navigation"]
        engine = self.game_state["engine"]
        env = self.game_state["environment"]["weather"]
        
        # Simple flight dynamics
        position = nav["position"]
        motion = nav["motion"]
        controls = nav["controls"]
        
        # Rudder physics - convert rudder angle to rate of turn
        rudder_angle = controls["rudder"]  # -30 to +30 degrees
        airspeed_factor = motion["indicatedAirspeed"] / 85.0  # Normalize to typical cruise speed
        
        # Rate of turn based on rudder (simplified aerodynamics)
        max_turn_rate = 3.0  # degrees per second at full rudder, cruise speed
        motion["rateOfTurn"] = (rudder_angle / 30.0) * max_turn_rate * airspeed_factor
        
        # Apply rate of turn to heading
        position["heading"] += motion["rateOfTurn"] * dt
        position["heading"] = position["heading"] % 360
        
        # Realistic thrust calculation based on actual engine performance and altitude
        if engine["running"]:
            # Get current altitude for air density calculations
            altitude = position["altitude"]
            altitude_density_factor = math.exp(-altitude / 29000.0)  # Air density decreases with altitude
            
            # Calculate thrust based on actual engine RPM and propeller efficiency
            max_rpm = 2800.0
            current_rpm = engine["rpm"]
            rpm_factor = current_rpm / max_rpm
            
            # Propeller efficiency curve (peak around 75% RPM)
            if rpm_factor < 0.2:
                base_prop_efficiency = rpm_factor * 2.0  # Poor efficiency at very low RPM
            elif rpm_factor < 0.75:
                base_prop_efficiency = 0.4 + (rpm_factor - 0.2) * 1.1  # Rising efficiency
            else:
                base_prop_efficiency = 1.0 - (rpm_factor - 0.75) * 0.4  # Declining past peak
                
            # Propeller pitch affects efficiency - optimal pitch varies with airspeed and altitude
            prop_pitch = engine["controls"]["propeller"]
            current_airspeed = motion["indicatedAirspeed"]
            
            # Optimal prop pitch for current conditions
            # At low airspeed: want lower pitch (fine pitch) for better acceleration
            # At high airspeed: want higher pitch (coarse pitch) for efficiency
            # At high altitude: want slightly lower pitch due to thinner air
            optimal_pitch_for_speed = 0.3 + (current_airspeed / 100.0) * 0.4  # 0.3-0.7 range
            optimal_pitch_for_altitude = optimal_pitch_for_speed * (0.9 + altitude_density_factor * 0.1)
            optimal_pitch_for_altitude = max(0.2, min(0.9, optimal_pitch_for_altitude))
            
            # Efficiency penalty for non-optimal pitch
            pitch_deviation = abs(prop_pitch - optimal_pitch_for_altitude)
            if pitch_deviation <= 0.1:
                pitch_efficiency = 1.0
            elif pitch_deviation <= 0.3:
                pitch_efficiency = 1.0 - (pitch_deviation - 0.1) * 1.5  # Linear falloff
            else:
                pitch_efficiency = 0.7 - (pitch_deviation - 0.3) * 0.5  # Steeper falloff
            pitch_efficiency = max(0.4, pitch_efficiency)  # Minimum 40% efficiency
            
            # Combined propeller efficiency
            prop_efficiency = base_prop_efficiency * pitch_efficiency
            
            # Altitude significantly affects propeller thrust
            # Propeller thrust is roughly proportional to air density
            altitude_thrust_factor = altitude_density_factor
            
            # Base thrust from throttle setting and RPM
            throttle_setting = engine["controls"]["throttle"]
            base_thrust = throttle_setting * rpm_factor * prop_efficiency * altitude_thrust_factor
            
            # Further reduce thrust if fuel flow is insufficient
            expected_fuel_flow = throttle_setting * 18.0 * 0.85  # Expected flow at mixture
            actual_fuel_flow = engine["fuelFlow"]
            fuel_flow_factor = min(1.0, actual_fuel_flow / max(0.1, expected_fuel_flow))
            
            # Final thrust factor combining all effects
            thrust_factor = base_thrust * fuel_flow_factor
            
            # Calculate target airspeed based on thrust
            # Base airspeed decreases with altitude due to reduced thrust
            sea_level_airspeed = 85.0  # Cruise airspeed at full power, sea level
            altitude_airspeed_factor = 0.7 + altitude_density_factor * 0.3  # 70-100% performance
            base_airspeed = sea_level_airspeed * altitude_airspeed_factor
            min_airspeed = 15.0   # Minimum flying speed (stall region)
            target_airspeed = min_airspeed + (base_airspeed - min_airspeed) * thrust_factor
            
        else:
            # Engine off - aircraft becomes a glider with significant drag
            # Apply continuous deceleration due to drag until the aircraft stops
            current_speed = motion["indicatedAirspeed"]
            if current_speed > 0.5:  # Above minimum threshold
                # Exponential decay with a lower bound that allows reaching zero
                target_airspeed = max(0.0, current_speed * 0.92 - 0.1)  # Subtract constant to reach zero
            else:
                # Below threshold - stop completely
                target_airspeed = 0.0
            
        # Airspeed changes with realistic acceleration/deceleration rates
        airspeed_diff = target_airspeed - motion["indicatedAirspeed"]
        
        # Different response rates for acceleration vs deceleration
        if airspeed_diff > 0:
            # Acceleration - slower, depends on available thrust
            accel_rate = 0.8 * dt if engine["running"] else 0.1 * dt
        else:
            # Deceleration - faster due to drag
            decel_rate = 1.5 * dt
            accel_rate = decel_rate
            
        motion["indicatedAirspeed"] += airspeed_diff * accel_rate
        motion["indicatedAirspeed"] = max(0.0, motion["indicatedAirspeed"])  # Prevent negative airspeed
        
        # True airspeed calculation accounting for altitude and temperature
        # TAS increases with altitude due to decreasing air density
        altitude = position["altitude"]
        altitude_density_factor = math.exp(-altitude / 29000.0)
        
        # At higher altitudes, TAS is higher than IAS for the same dynamic pressure
        # This is a simplified relationship: TAS = IAS / sqrt(density_ratio)
        tas_factor = 1.0 / math.sqrt(altitude_density_factor)
        motion["trueAirspeed"] = motion["indicatedAirspeed"] * tas_factor
        
        # Ground speed affected by wind
        wind_component = env["windSpeed"] * math.cos(
            math.radians(position["heading"] - env["windDirection"])
        )
        motion["groundSpeed"] = motion["trueAirspeed"] + wind_component
        
        # Position updates based on ground speed and heading
        if motion["groundSpeed"] > 0:
            # Convert knots to degrees per second (very approximate)
            degrees_per_second = motion["groundSpeed"] / 3600.0 / 60.0
            
            heading_rad = math.radians(position["heading"])
            lat_change = degrees_per_second * math.cos(heading_rad) * dt
            lon_change = degrees_per_second * math.sin(heading_rad) * dt / math.cos(math.radians(position["latitude"]))
            
            position["latitude"] += lat_change
            position["longitude"] += lon_change
            
        # Autopilot handling
        if nav["autopilot"]["engaged"]:
            self._update_autopilot(dt)
            
    def _update_autopilot(self, dt: float):
        """Update autopilot systems"""
        nav = self.game_state["navigation"]
        autopilot = nav["autopilot"]
        position = nav["position"]
        targets = nav["targets"]
        controls = nav["controls"]
        motion = nav["motion"]
        
        # Heading hold with discrete rudder control (like manual input)
        if autopilot["headingHold"]:
            # For route follow mode, calculate bearing to waypoint as target heading
            if nav.get("mode") == "route_follow":
                waypoint_bearing = self.calculate_bearing_to_waypoint()
                if waypoint_bearing is not None:
                    target_heading = waypoint_bearing
                    # Update the targets heading so it shows correctly in displays
                    targets["heading"] = target_heading
                else:
                    # No waypoint, fall back to current target heading
                    target_heading = targets["heading"]
            else:
                # Normal heading hold mode
                target_heading = targets["heading"]
            
            heading_error = target_heading - position["heading"]
            # Normalize to -180 to +180
            while heading_error > 180:
                heading_error -= 360
            while heading_error < -180:
                heading_error += 360
                
            autopilot["headingError"] = heading_error
            
            # Discrete rudder adjustments based on heading error
            abs_error = abs(heading_error)
            current_rudder = controls["rudder"]
            
            # Determine target rudder adjustment based on error magnitude
            if abs_error > 20:
                # Large error: aggressive correction
                target_rudder_step = 2.0 if heading_error > 0 else -2.0
            elif abs_error > 10:
                # Medium error: moderate correction
                target_rudder_step = 2.0 if heading_error > 0 else -2.0
            elif abs_error > 2:
                # Small error: gentle correction
                target_rudder_step = 2.0 if heading_error > 0 else -2.0
            else:
                # Very close to target: center the rudder
                if abs(current_rudder) >= 2.0:
                    target_rudder_step = -2.0 if current_rudder > 0 else 2.0
                else:
                    target_rudder_step = -current_rudder  # Final centering step
            
            # Apply discrete rudder adjustment at autopilot rate (slower than manual)
            # Autopilot makes adjustments every 0.5 seconds instead of instantly
            if "lastRudderAdjust" not in autopilot:
                autopilot["lastRudderAdjust"] = 0.0
                
            autopilot["lastRudderAdjust"] += dt
            
            if autopilot["lastRudderAdjust"] >= 0.5:  # Adjust every 0.5 seconds
                # Apply the discrete step
                new_rudder = current_rudder + target_rudder_step
                controls["rudder"] = max(-30.0, min(30.0, new_rudder))
                autopilot["lastRudderAdjust"] = 0.0
                
                # Store autopilot debug info
                autopilot["targetRudderStep"] = target_rudder_step
                autopilot["turnRate"] = target_rudder_step / 2.0  # Approximate turn rate
                
        # Altitude hold with smooth easing
        if autopilot["altitudeHold"] or nav.get("mode") in ["heading_hold", "route_follow"]:
            current_altitude = position["altitude"]
            target_altitude = targets["altitude"]
            altitude_error = target_altitude - current_altitude
            
            # Smooth altitude control with easing
            abs_error = abs(altitude_error)
            
            # Define approach phases with different characteristics
            if abs_error > 200:
                # Far from target: steady climb/descent rate
                base_rate = 150.0  # ft/min (reasonable for airship)
            elif abs_error > 50:
                # Medium distance: moderate rate
                base_rate = 80.0   # ft/min
            elif abs_error > 10:
                # Close to target: gentle approach
                base_rate = 30.0   # ft/min
            else:
                # Very close: fine adjustment with easing
                base_rate = 10.0   # ft/min
                
            # Apply proportional control with easing near target
            if abs_error <= 25:
                # Easing zone: gradual slowdown as we approach target
                easing_factor = abs_error / 25.0  # 0.0 to 1.0
                # Use smooth ease-out curve
                easing_factor = 1.0 - (1.0 - easing_factor) ** 3
                climb_rate_fpm = base_rate * easing_factor
            else:
                # Normal zone: consistent rate
                climb_rate_fpm = base_rate
                
            # Apply direction
            if altitude_error < 0:
                climb_rate_fpm = -climb_rate_fpm
                
            # Convert to feet per second and apply
            climb_rate_fps = climb_rate_fpm / 60.0
            position["altitude"] += climb_rate_fps * dt
            motion["verticalSpeed"] = climb_rate_fpm
            
            # Ensure we don't overshoot significantly
            new_error = targets["altitude"] - position["altitude"]
            if abs(new_error) < 1.0:
                # Snap to target when very close
                position["altitude"] = targets["altitude"]
                motion["verticalSpeed"] = 0.0
            
    def _update_fuel_system(self, dt: float):
        """Update two-tank fuel system: feed, transfer, dump, and effect on attitude/speed"""
        fuel = self.game_state["fuel"]
        engine = self.game_state["engine"]
        nav_motion = self.game_state["navigation"]["motion"]

        forward = fuel["tanks"]["forward"]
        aft = fuel["tanks"]["aft"]

        # Engine consumption only if at least one tank feeding
        feed_tanks = [t for t in (forward, aft) if t["feed"] and t["level"] > 0.01]
        fuel["engineFeedCut"] = len(feed_tanks) == 0
        if engine["running"] and not fuel["engineFeedCut"]:
            per_tank = (engine["fuelFlow"] * dt / 3600.0) / len(feed_tanks)
            for tank in feed_tanks:
                tank["level"] = max(0.0, tank["level"] - per_tank)
        elif engine["running"] and fuel["engineFeedCut"]:
            # Starved engine: rapidly lose RPM & fuelFlow
            engine["rpm"] = max(0.0, engine["rpm"] - 800.0 * dt)
            engine["fuelFlow"] = max(0.0, engine["fuelFlow"] - 30.0 * dt)

        # Transfer pumps: rate scale (transferRate 0..1) * maxTransferGPH
        # Max rate empties 180g tank in 60 seconds: 180g / (60s / 3600s/h) = 10,800 GPH
        max_transfer_gph = 10800.0  # High flow rate for rapid tank-to-tank transfers
        # Forward -> Aft
        if forward["transferRate"] > 0 and forward["level"] > 0.01 and aft["level"] < aft["capacity"] - 0.01:
            gal = min(forward["level"], (forward["transferRate"] * max_transfer_gph) * dt / 3600.0)
            # Don't overfill aft
            gal = min(gal, aft["capacity"] - aft["level"])
            forward["level"] -= gal
            aft["level"] += gal
        # Aft -> Forward
        if aft["transferRate"] > 0 and aft["level"] > 0.01 and forward["level"] < forward["capacity"] - 0.01:
            gal = min(aft["level"], (aft["transferRate"] * max_transfer_gph) * dt / 3600.0)
            gal = min(gal, forward["capacity"] - forward["level"])
            aft["level"] -= gal
            forward["level"] += gal

        # Dump pumps: remove fuel overboard (same 60-second emptying rate)
        max_dump_gph = 10800.0  # Match transfer rate for consistent emptying time
        if forward["dumpRate"] > 0 and forward["level"] > 0.01:
            dump = min(forward["level"], (forward["dumpRate"] * max_dump_gph) * dt / 3600.0)
            forward["level"] -= dump
        if aft["dumpRate"] > 0 and aft["level"] > 0.01:
            dump = min(aft["level"], (aft["dumpRate"] * max_dump_gph) * dt / 3600.0)
            aft["level"] -= dump

        # Clamp levels
        forward["level"] = max(0.0, min(forward["capacity"], forward["level"]))
        aft["level"] = max(0.0, min(aft["capacity"], aft["level"]))

        # Update aggregate fuel value
        fuel["currentLevel"] = forward["level"] + aft["level"]

        # Balance & attitude effects: pitch based on difference
        # Difference ratio (-1..+1) (aft heavy positive -> nose up) we want forward heavy nose down maybe.
        diff = aft["level"] - forward["level"]  # +ve means aft heavier
        max_diff = forward["capacity"]  # scale reference
        imbalance_ratio = max(-1.0, min(1.0, diff / max_diff))
        # Max +/-10 deg pitch
        target_pitch = imbalance_ratio * 10.0
        # Smooth pitch change
        current_pitch = nav_motion.get("pitch", 0.0)
        pitch_diff = target_pitch - current_pitch
        nav_motion["pitch"] = current_pitch + pitch_diff * min(1.0, 2.0 * dt)

        # Aerodynamic drag penalty for imbalance: reduce indicated airspeed
        base_speed = nav_motion.get("indicatedAirspeed", 0.0)
        penalty_factor = 1.0 - (abs(imbalance_ratio) * 0.15)  # up to 15% loss
        nav_motion["indicatedAirspeed"] = base_speed * penalty_factor
        # True airspeed recalculated next nav update; we tweak here only indicated
            
    def _update_electrical_system(self, dt: float):
        """Update electrical system simulation"""
        electrical = self.game_state["electrical"]
        engine = self.game_state["engine"]
        
        # Calculate total electrical load
        total_load = sum(electrical["loads"].values())
        
        # Alternator output when engine running
        if engine["running"] and engine["rpm"] > 1000:
            alternator = electrical["alternator"]
            alternator["online"] = True
            # Output varies with RPM
            rpm_factor = min(1.0, engine["rpm"] / 2000.0)
            alternator["current"] = min(alternator["maxOutput"], total_load * 1.2) * rpm_factor
            alternator["voltage"] = 14.2 if rpm_factor > 0.8 else 12.8
        else:
            electrical["alternator"]["online"] = False
            electrical["alternator"]["current"] = 0.0
            electrical["alternator"]["voltage"] = 0.0
            
        # Battery discharge/charge
        net_current = electrical["alternator"]["current"] - total_load
        
        for battery_name in ["batteryBusA", "batteryBusB"]:
            battery = electrical[battery_name]
            if battery["switch"]:
                if net_current > 0:
                    # Charging
                    charge_rate = min(net_current / 2, 10.0)  # Max 10A charge rate
                    battery["remaining"] = min(battery["capacity"], 
                                             battery["remaining"] + charge_rate * dt / 3600.0)
                    battery["voltage"] = 12.6 if battery["remaining"] > battery["capacity"] * 0.8 else 12.3
                else:
                    # Discharging
                    discharge_rate = abs(net_current) / 2  # Split load between batteries
                    battery["remaining"] = max(0, battery["remaining"] - discharge_rate * dt / 3600.0)
                    
                    # Voltage drops as battery depletes
                    charge_percent = battery["remaining"] / battery["capacity"]
                    if charge_percent > 0.5:
                        battery["voltage"] = 12.6
                    elif charge_percent > 0.2:
                        battery["voltage"] = 12.3
                    else:
                        battery["voltage"] = 11.8
                        
                battery["current"] = discharge_rate if net_current < 0 else 0
                
    def _update_environment(self, dt: float):
        """Update environmental conditions"""
        env = self.game_state["environment"]
        
        # Update time
        env["time"]["utc"] += dt
        env["time"]["local"] = env["time"]["utc"]  # Simplified
        
        # Simple weather changes (very gradual)
        weather = env["weather"]
        
        # Wind can shift slightly
        weather["windDirection"] += (math.sin(self.total_sim_time * 0.01) * 0.1)
        weather["windDirection"] = weather["windDirection"] % 360
        
    def _update_systems_monitoring(self, dt: float):
        """Monitor systems and generate warnings/alerts"""
        systems = self.game_state["systems"]
        engine = self.game_state["engine"]
        fuel = self.game_state["fuel"]
        electrical = self.game_state["electrical"]
        
        # Clear old warnings
        systems["warnings"] = []
        systems["alerts"] = []
        
        # Engine warnings
        if engine["running"]:
            if engine["oilPressure"] < 25:
                systems["warnings"].append("LOW OIL PRESSURE")
            if engine["oilTemperature"] > 240:
                systems["warnings"].append("HIGH OIL TEMPERATURE")
            if engine["cylinderHeadTemp"] > 400:
                systems["warnings"].append("HIGH CYLINDER HEAD TEMP")
                
        # Fuel warnings
        if fuel["currentLevel"] < 50:
            systems["warnings"].append("LOW FUEL")
        if fuel["currentLevel"] < 20:
            systems["alerts"].append("CRITICAL FUEL")
            
        # Electrical warnings
        for battery_name in ["batteryBusA", "batteryBusB"]:
            battery = electrical[battery_name]
            if battery["switch"] and battery["remaining"] < 5:
                systems["warnings"].append(f"LOW BATTERY {battery_name[-1]}")
                
    def _approach_value(self, current: float, target: float, rate: float) -> float:
        """Helper to gradually approach a target value"""
        diff = target - current
        if abs(diff) <= rate:
            return diff
        return rate if diff > 0 else -rate
    
    def _update_cargo_system(self, dt: float):
        """Update cargo system - winch movement and loading bay availability"""
        cargo = self.game_state.get("cargo", {})
        winch = cargo.get("winch", {})
        movement = winch.get("movementState", {})
        
        # Update winch position based on movement state
        winch_speed = 50.0  # pixels per second
        cable_speed = 80.0  # pixels per second
        
        current_pos = winch.get("position", {"x": 160, "y": 50})
        current_cable = winch.get("cableLength", 0)
        
        # Horizontal movement
        if movement.get("left", False):
            new_x = current_pos["x"] - winch_speed * dt
            self.set_winch_position(new_x, current_pos["y"])
        elif movement.get("right", False):
            new_x = current_pos["x"] + winch_speed * dt
            self.set_winch_position(new_x, current_pos["y"])
        
        # Vertical cable movement
        if movement.get("up", False):
            new_cable = current_cable - cable_speed * dt
            self.set_cable_length(new_cable)
        elif movement.get("down", False):
            new_cable = current_cable + cable_speed * dt
            self.set_cable_length(new_cable)
        
        # Check if ship is moving under power and handle loading bay
        # Use indicated airspeed instead of ground speed to avoid wind drift triggering clearing
        indicated_airspeed = self.game_state.get("navigation", {}).get("motion", {}).get("indicatedAirspeed", 0.0)
        
        if indicated_airspeed > 0.1:
            # Ship is actively moving under power - disable refresh and clear loading bay
            cargo["refreshAvailable"] = False
            if cargo.get("loadingBay"):
                cargo["loadingBay"] = []
        else:
            # Ship is stopped (not moving under power) - enable refresh
            cargo["refreshAvailable"] = True

        # If a crate is attached, move it with the hook position (centered & snapped)
        attached_id = winch.get("attachedCrate")
        if attached_id:
            crate = self._find_crate_by_id(attached_id)
            if crate:
                crate_type = crate.get("type", "")
                info = cargo.get("crateTypes", {}).get(crate_type, {})
                dims = info.get("dimensions", {"width": 1, "height": 1})
                w_px = max(1, dims.get("width", 1)) * CARGO_GRID_PX
                h_px = max(1, dims.get("height", 1)) * CARGO_GRID_PX
                hook_x = winch.get("position", {}).get("x", 160)
                hook_y = winch.get("position", {}).get("y", 50) + winch.get("cableLength", 0)
                # Position crate so hook attaches to top-center of crate
                x = int(round((hook_x - w_px // 2) / CARGO_GRID_PX) * CARGO_GRID_PX)
                y = int(round(hook_y / CARGO_GRID_PX) * CARGO_GRID_PX)  # Hook at top of crate
                # Clamp within whichever area the x is in
                area_name, bounds = self._area_bounds_for(x, w_px, h_px)
                min_x, max_x, min_y, max_y = bounds
                x = max(min_x, min(max_x, x))
                y = max(min_y, min(max_y, y))
                crate["position"] = {"x": x, "y": y}
        
    def get_state(self) -> Dict[str, Any]:
        """Get the current game state (read-only access)"""
        return self.game_state.copy()
        
    def set_engine_control(self, control: str, value: float):
        """Set engine control position"""
        if control in ["throttle", "mixture", "propeller"]:
            self.game_state["engine"]["controls"][control] = max(0.0, min(1.0, value))
            
    def toggle_engine(self):
        """Toggle engine on/off"""
        engine = self.game_state["engine"]
        if engine["running"]:
            engine["running"] = False
        else:
            engine["running"] = True
            engine["emergencyShutdown"] = False
            
    def set_autopilot_target(self, parameter: str, value: float):
        """Set autopilot target values"""
        targets = self.game_state["navigation"]["targets"]
        autopilot = self.game_state["navigation"]["autopilot"]
        
        if parameter in targets:
            targets[parameter] = value
            
            # Auto-enable appropriate autopilot modes when targets are set
            if parameter == "altitude":
                # Setting altitude target enables altitude hold
                autopilot["altitudeHold"] = True
                autopilot["engaged"] = True
            elif parameter == "heading":
                # Setting heading target enables heading hold
                autopilot["headingHold"] = True  
                autopilot["engaged"] = True
            
    def toggle_autopilot_mode(self, mode: str):
        """Toggle autopilot modes"""
        autopilot = self.game_state["navigation"]["autopilot"]
        if mode in autopilot:
            autopilot[mode] = not autopilot[mode]
            autopilot["engaged"] = any(autopilot[key] for key in ["headingHold", "altitudeHold", "airspeedHold"])
            
    def set_nav_mode(self, mode: str):
        """Set navigation mode"""
        if mode in ["manual", "heading_hold", "altitude_hold", "route_follow"]:
            nav = self.game_state["navigation"]
            nav["mode"] = mode
            
            # Navigation mode just sets the mode - autopilot engagement is separate
            # The pilot must manually engage the autopilot using the AP button
            
    def toggle_battery(self, battery: str = "A"):
        """Toggle battery switch"""
        battery_key = f"batteryBus{battery}"
        if battery_key in self.game_state["electrical"]:
            battery_obj = self.game_state["electrical"][battery_key]
            battery_obj["switch"] = not battery_obj["switch"]
            
    def toggle_fuel_pump_mode(self):
        """Toggle fuel pump mode"""
        # Legacy - no-op after refactor
        pass

    # --- New Fuel Control Interface ---
    def set_tank_feed(self, tank: str, feed: bool):
        if tank in self.game_state["fuel"]["tanks"]:
            self.game_state["fuel"]["tanks"][tank]["feed"] = bool(feed)

    def set_transfer_rate(self, tank: str, rate: float):
        if tank in self.game_state["fuel"]["tanks"]:
            self.game_state["fuel"]["tanks"][tank]["transferRate"] = max(0.0, min(1.0, rate))

    def set_dump_rate(self, tank: str, rate: float):
        if tank in self.game_state["fuel"]["tanks"]:
            self.game_state["fuel"]["tanks"][tank]["dumpRate"] = max(0.0, min(1.0, rate))
        
    def adjust_rudder(self, degrees: float):
        """Adjust rudder position by the specified degrees (manual control)"""
        nav = self.game_state["navigation"]
        controls = nav["controls"]
        
        # Only allow manual rudder in manual mode
        if nav.get("mode", "manual") == "manual":
            # Adjust rudder by the specified amount
            new_rudder = controls["rudder"] + degrees
            
            # Clamp to realistic limits (-30 to +30 degrees)
            controls["rudder"] = max(-30.0, min(30.0, new_rudder))
        
    def apply_rudder_input(self, input_strength: float):
        """Apply continuous rudder input (for autopilot use)"""
        nav = self.game_state["navigation"]
        
        # Set rudder directly (used by autopilot)
        max_rudder = 30.0  # Maximum rudder deflection in degrees
        target_rudder = input_strength * max_rudder
        
        # Apply rudder input with some smoothing
        current_rudder = nav["controls"]["rudder"]
        rudder_rate = 60.0  # degrees per second rudder movement rate
        
        # Move rudder towards target
        if abs(target_rudder - current_rudder) > 0.1:
            if target_rudder > current_rudder:
                nav["controls"]["rudder"] = min(target_rudder, current_rudder + rudder_rate * 0.1)
            else:
                nav["controls"]["rudder"] = max(target_rudder, current_rudder - rudder_rate * 0.1)
        else:
            nav["controls"]["rudder"] = target_rudder
                
    def toggle_main_autopilot(self):
        """Toggle main autopilot engagement"""
        nav = self.game_state["navigation"]
        autopilot = nav["autopilot"]
        current_mode = nav.get("mode", "manual")
        
        if autopilot["engaged"]:
            # Disengage autopilot - turn off all modes
            autopilot["engaged"] = False
            autopilot["headingHold"] = False
            autopilot["altitudeHold"] = False
        else:
            # Engage autopilot based on current navigation mode
            autopilot["engaged"] = True
            
            if current_mode == "heading_hold":
                autopilot["headingHold"] = True
                autopilot["altitudeHold"] = False
                # Set current heading as target if not already set
                if nav["targets"]["heading"] == 0:  # Default value
                    nav["targets"]["heading"] = nav["position"]["heading"]
            elif current_mode == "altitude_hold":
                autopilot["headingHold"] = False
                autopilot["altitudeHold"] = True
                # Set current altitude as target if not already set
                if nav["targets"]["altitude"] == 0:  # Default value
                    nav["targets"]["altitude"] = nav["position"]["altitude"]
            elif current_mode == "route_follow":
                autopilot["headingHold"] = True
                autopilot["altitudeHold"] = True
            else:
                # Manual mode - autopilot disengaged
                autopilot["engaged"] = False

    def set_navigation_view(self, zoom_level: float, offset_x: float, offset_y: float):
        """Set navigation map view settings (zoom and pan)"""
        nav = self.game_state["navigation"]
        
        # Initialize mapView if it doesn't exist (for backwards compatibility with old saves)
        if "mapView" not in nav:
            nav["mapView"] = {
                "zoomLevel": 1.0,
                "offsetX": 0.0,
                "offsetY": 0.0
            }
            
        map_view = nav["mapView"]
        
        # Clamp zoom level to reasonable bounds
        map_view["zoomLevel"] = max(0.25, min(4.0, zoom_level))
        map_view["offsetX"] = offset_x
        map_view["offsetY"] = offset_y
        
    def get_navigation_view(self) -> Dict[str, float]:
        """Get current navigation map view settings"""
        nav = self.game_state["navigation"]
        
        # Initialize mapView if it doesn't exist (for backwards compatibility with old saves)
        if "mapView" not in nav:
            nav["mapView"] = {
                "zoomLevel": 1.0,
                "offsetX": 0.0,
                "offsetY": 0.0
            }
            
        return nav["mapView"].copy()

    # === CARGO SYSTEM METHODS ===
    
    def get_cargo_state(self) -> Dict[str, Any]:
        """Get current cargo system state"""
        return self.game_state.get("cargo", {})
    
    def set_winch_position(self, x: float, y: float):
        """Set winch position along the rail"""
        cargo = self.game_state.get("cargo", {})
        if "winch" not in cargo:
            cargo["winch"] = {"position": {"x": 160, "y": 50}, "cableLength": 0, "attachedCrate": None, "movementState": {}}
        
        # Clamp to rail limits (8 to 312 for 320 width screen)
        cargo["winch"]["position"]["x"] = max(8, min(312, x))
        cargo["winch"]["position"]["y"] = y
    
    def set_cable_length(self, length: float):
        """Set winch cable length"""
        cargo = self.game_state.get("cargo", {})
        if "winch" not in cargo:
            cargo["winch"] = {"position": {"x": 160, "y": 50}, "cableLength": 0, "attachedCrate": None, "movementState": {}}
        
        # Clamp to reasonable limits (0 to 200 pixels)
        cargo["winch"]["cableLength"] = max(0, min(200, length))
    
    def set_winch_movement_state(self, direction: str, active: bool):
        """Set winch movement state for continuous movement"""
        cargo = self.game_state.get("cargo", {})
        if "winch" not in cargo:
            cargo["winch"] = {"position": {"x": 160, "y": 50}, "cableLength": 0, "attachedCrate": None, "movementState": {}}
        
        # Ensure movementState has all required keys
        if "movementState" not in cargo["winch"] or not cargo["winch"]["movementState"]:
            cargo["winch"]["movementState"] = {"left": False, "right": False, "up": False, "down": False}
        else:
            # Ensure all direction keys exist
            required_keys = ["left", "right", "up", "down"]
            for key in required_keys:
                if key not in cargo["winch"]["movementState"]:
                    cargo["winch"]["movementState"][key] = False
        
        if direction in cargo["winch"]["movementState"]:
            cargo["winch"]["movementState"][direction] = active
    
    def attach_crate(self, crate_id: str) -> bool:
        """Attach crate to winch cable"""
        cargo = self.game_state.get("cargo", {})
        winch = cargo.get("winch", {})
        
        # Find crate in either area
        crate = None
        for area_name in ["cargoHold", "loadingBay"]:
            for c in cargo.get(area_name, []):
                if c.get("id") == crate_id:
                    crate = c
                    break
            if crate:
                break
        
        if crate and not winch.get("attachedCrate"):
            winch["attachedCrate"] = crate_id
            return True
        return False
    
    def detach_crate(self) -> bool:
        """Detach crate from winch cable"""
        cargo = self.game_state.get("cargo", {})
        winch = cargo.get("winch", {})
        
        if winch.get("attachedCrate"):
            crate_id = winch["attachedCrate"]
            
            # Check if placement is allowed (this handles moving ship restrictions)
            if not self.can_place_attached_crate():
                return False
                
            # Find the attached crate and get settled placement
            settle = self._compute_settled_position_for_attached_crate()
            if settle:
                area_name, position = settle
                
                # Get the crate data (either from attachedCrateData or from areas)
                crate = None
                attached_crate_data = cargo.get("attachedCrateData", {})
                
                if crate_id in attached_crate_data:
                    # It's an attached crate (like books from library)
                    crate = attached_crate_data.pop(crate_id)
                else:
                    # Remove from any existing area
                    for area in ["cargoHold", "loadingBay"]:
                        for i, c in enumerate(cargo.get(area, [])):
                            if c.get("id") == crate_id:
                                crate = cargo[area].pop(i)
                                break
                        if crate:
                            break
                
                if crate is None:
                    return False
                    
                crate["position"] = position
                cargo.setdefault(area_name, []).append(crate)
                winch["attachedCrate"] = None
                self._update_cargo_physics()
                return True
        return False
    
    def move_crate(self, crate_id: str, area: str, position: Dict[str, float]):
        """Move crate to new area and position"""
        cargo = self.game_state.get("cargo", {})
        
        # Remove crate from current area
        crate = None
        for area_name in ["cargoHold", "loadingBay"]:
            for i, c in enumerate(cargo.get(area_name, [])):
                if c.get("id") == crate_id:
                    crate = cargo[area_name].pop(i)
                    break
            if crate:
                break
        
        if crate and area in ["cargoHold", "loadingBay"]:
            crate["position"] = position
            cargo[area].append(crate)
            self._update_cargo_physics()
    
    def use_crate(self, crate_id: str) -> bool:
        """Use/consume a crate and apply its effects"""
        cargo = self.game_state.get("cargo", {})
        
        # Find crate in cargo hold or loading bay
        crate = None
        crate_index = None
        area = None
        
        # Check cargo hold first
        for i, c in enumerate(cargo.get("cargoHold", [])):
            if c.get("id") == crate_id:
                crate = c
                crate_index = i
                area = "cargoHold"
                break
        
        # If not found in cargo hold, check loading bay
        if not crate:
            for i, c in enumerate(cargo.get("loadingBay", [])):
                if c.get("id") == crate_id:
                    crate = c
                    crate_index = i
                    area = "loadingBay"
                    break
        
        if not crate:
            return False
        
        crate_type = crate.get("type", "")
        crate_info = cargo.get("crateTypes", {}).get(crate_type, {})
        
        if not crate_info.get("usable"):
            return False
        
        # Apply use action
        use_action = crate_info.get("useAction", "")
        success = False
        
        if use_action == "transfer_fuel":
            gallons = crate.get("contents", {}).get("amount", 0)
            self.add_fuel_to_tanks(gallons)
            success = True
        elif use_action == "add_medical_supplies":
            success = True
        elif use_action == "add_food":
            success = True
        elif use_action == "add_to_library":
            # Harmonized: add the specific book to the library using book_id
            book_id = crate.get("book_id")
            if book_id:
                self.add_in_game_book_to_library(book_id)
                success = True
            else:
                success = False
        
        if success and crate_index is not None:
            # Remove used crate from the appropriate area
            cargo[area].pop(crate_index)
            self._update_cargo_physics()
        
        return success
    
    def refresh_loading_bay(self):
        """Generate new random cargo in loading bay"""
        cargo = self.game_state.get("cargo", {})
        
        # Only refresh if ship is not moving under power and refresh is available
        # Use indicated airspeed instead of ground speed to avoid wind drift issues
        indicated_airspeed = self.game_state.get("navigation", {}).get("motion", {}).get("indicatedAirspeed", 0.0)
        if indicated_airspeed > 0.1 or not cargo.get("refreshAvailable", True):
            return
        
        # Clear loading bay but preserve attached crates
        winch = cargo.get("winch", {})
        attached_crate_id = winch.get("attachedCrate")
        
        if attached_crate_id:
            # Keep only the attached crate, remove others
            loading_bay = cargo.get("loadingBay", [])
            cargo["loadingBay"] = [crate for crate in loading_bay 
                                 if crate.get("id") == attached_crate_id]
        else:
            # No attached crate, clear entire loading bay
            cargo["loadingBay"] = []
        
        # Generate 2-4 random crates
        crate_types = list(cargo.get("crateTypes", {}).keys())
        
        # Safety check: ensure we have crate types available
        if not crate_types:
            print("⚠️ No crate types available for loading bay refresh")
            return
            
        num_crates = random.randint(2, 4)
        
        for i in range(num_crates):
            crate_type = random.choice(crate_types)
            crate_info = cargo["crateTypes"][crate_type]
            position = self._find_valid_loading_bay_position(crate_info["dimensions"])
            if position:
                crate = {
                    "id": f"crate_{int(time.time() * 1000)}_{i}",
                    "type": crate_type,
                    "position": position,
                    "contents": crate_info["contents"].copy()
                }
                # If this is a book crate, assign a random in-game book_id
                if crate_type == "books":
                    in_game_books = self._scan_in_game_books()
                    if in_game_books:
                        crate["book_id"] = random.choice(in_game_books)["id"]
                cargo["loadingBay"].append(crate)
    
    def can_place_attached_crate(self) -> bool:
        """Public: can the currently attached crate be placed (after settling)?"""
        settle = self._compute_settled_position_for_attached_crate()
        if settle is None:
            return False
            
        area_name, position = settle
        
        # Check if ship is moving and would place in loading bay
        indicated_airspeed = self.game_state.get("navigation", {}).get("motion", {}).get("indicatedAirspeed", 0.0)
        if indicated_airspeed > 0.1 and area_name == "loadingBay":
            # Cannot detach into loading bay while moving
            return False
            
        return True

    def _can_place_attached_crate(self) -> bool:
        """Deprecated internal: use can_place_attached_crate"""
        return self.can_place_attached_crate()

    def _compute_settled_position_for_attached_crate(self) -> Optional[Tuple[str, Dict[str, int]]]:
        """Compute final settled top-left position if we detach now; return (area, pos) or None."""
        cargo = self.game_state.get("cargo", {})
        winch = cargo.get("winch", {})
        
        if not winch.get("attachedCrate"):
            return None
        
        # Get crate info
        crate_id = winch["attachedCrate"]
        crate = self._find_crate_by_id(crate_id)
        if not crate:
            return None
        
        # Calculate crate position based on winch and cable
        winch_pos = winch.get("position", {})
        cable_length = winch.get("cableLength", 0)
        # Center the crate horizontally under the hook based on its width
        crate_type = crate.get("type", "")
        crate_info = cargo.get("crateTypes", {}).get(crate_type, {})
        dimensions = crate_info.get("dimensions", {"width": 1, "height": 1})
        w_px = max(1, dimensions.get("width", 1)) * CARGO_GRID_PX
        h_px = max(1, dimensions.get("height", 1)) * CARGO_GRID_PX
        hook_x = winch_pos.get("x", 160)
        hook_y = 52 + cable_length  # rail y is 52
        x0 = int(round((hook_x - w_px // 2) / CARGO_GRID_PX) * CARGO_GRID_PX)
        y0 = int(round(hook_y / CARGO_GRID_PX) * CARGO_GRID_PX)  # Hook at top of crate

        # Clamp x,y to area and determine area bounds
        area_name, bounds = self._area_bounds_for(x0, w_px, h_px)
        if area_name is None:
            return None
        min_x, max_x, min_y, max_y = bounds
        x = max(min_x, min(max_x, x0))
        # Drop straight down until collision would occur or floor
        best_y = None
        # Clamp initial y into [min_y, max_y] so scan always executes
        y = max(min_y, min(max_y, y0))
        # Iterate downwards by grid cells, default to floor when no collision
        collided = False
        while y <= max_y:
            if self._check_crate_collision({"x": x, "y": y}, dimensions, exclude_id=crate_id):
                collided = True
                break
            y += CARGO_GRID_PX
        if collided:
            best_y = y - CARGO_GRID_PX
        else:
            best_y = max_y
        # At best_y we are non-overlapping. Ensure support: either floor or crates under both corners
        bottom_y = best_y + h_px
        if bottom_y >= (60 + 180):  # floor (updated from 200 to 180)
            return area_name, {"x": x, "y": best_y}
        if self._has_corner_support(x, best_y, w_px, h_px):
            return area_name, {"x": x, "y": best_y}
        return None
    
    def _find_crate_by_id(self, crate_id: str):
        """Find crate by ID in any area or attached to winch"""
        cargo = self.game_state.get("cargo", {})
        
        # First check if it's an attached crate
        attached_crate_data = cargo.get("attachedCrateData", {})
        if crate_id in attached_crate_data:
            return attached_crate_data[crate_id]
        
        # Then check normal areas
        for area_name in ["cargoHold", "loadingBay"]:
            for crate in cargo.get(area_name, []):
                if crate.get("id") == crate_id:
                    return crate
        return None
    
    def _is_position_in_valid_area(self, position: Dict[str, float], dimensions: Dict[str, int]) -> bool:
        """Check if crate rectangle is fully within cargo hold or loading bay"""
        x, y = position.get("x", 0), position.get("y", 0)
        w_px = max(1, dimensions.get("width", 1)) * CARGO_GRID_PX
        h_px = max(1, dimensions.get("height", 1)) * CARGO_GRID_PX
        # Cargo hold bounds (updated height from 200 to 180)
        hold_x, hold_y, hold_w, hold_h = 8, 60, 150, 180
        bay_x, bay_y, bay_w, bay_h = 162, 60, 150, 180
        if (hold_x <= x and x + w_px <= hold_x + hold_w and
            hold_y <= y and y + h_px <= hold_y + hold_h):
            return True
        if (bay_x <= x and x + w_px <= bay_x + bay_w and
            bay_y <= y and y + h_px <= bay_y + bay_h):
            return True
        return False
    
    def _check_crate_collision(self, position: Dict[str, float], dimensions: Dict[str, int], exclude_id: str = None) -> bool:
        """Check if crate would collide with existing crates"""
        cargo = self.game_state.get("cargo", {})
        
        x1, y1 = position.get("x", 0), position.get("y", 0)
        w1, h1 = dimensions.get("width", 1) * CARGO_GRID_PX, dimensions.get("height", 1) * CARGO_GRID_PX
        
        for area_name in ["cargoHold", "loadingBay"]:
            for crate in cargo.get(area_name, []):
                if exclude_id and crate.get("id") == exclude_id:
                    continue
                
                crate_pos = crate.get("position", {})
                x2, y2 = crate_pos.get("x", 0), crate_pos.get("y", 0)
                
                crate_type = crate.get("type", "")
                crate_info = cargo.get("crateTypes", {}).get(crate_type, {})
                crate_dims = crate_info.get("dimensions", {"width": 1, "height": 1})
                w2, h2 = crate_dims.get("width", 1) * CARGO_GRID_PX, crate_dims.get("height", 1) * CARGO_GRID_PX
                
                # AABB collision detection
                if not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1):
                    return True
        
        return False
    
    def _find_valid_loading_bay_position(self, dimensions: Dict[str, int]) -> Dict[str, float]:
        """Find a valid position in loading bay for new crate"""
        # Loading bay bounds (snap to grid)
        width_px = dimensions.get("width", 1) * CARGO_GRID_PX
        height_px = dimensions.get("height", 1) * CARGO_GRID_PX
        
        # Loading bay area: x=162, y=60, width=150, height=180
        # So area goes from (162,60) to (312,240)
        # For crate placement, top-left corner constraints:
        min_x = 162
        max_x = 312 - width_px  # Ensure crate right edge doesn't exceed 312
        min_y = 60  # Top of loading bay
        max_y = 240 - height_px  # Ensure crate bottom doesn't exceed 240 (floor level)
        
        # Try random positions
        for _ in range(50):  # Max attempts
            # choose grid-aligned positions
            gx_min = (min_x + CARGO_GRID_PX - 1) // CARGO_GRID_PX  # Round up
            gx_max = (max_x // CARGO_GRID_PX)
            gy_min = (min_y + CARGO_GRID_PX - 1) // CARGO_GRID_PX  # Round up  
            gy_max = (max_y // CARGO_GRID_PX)
            
            # Ensure we have valid grid ranges
            if gx_max < gx_min or gy_max < gy_min:
                continue
                
            x = random.randint(gx_min, gx_max) * CARGO_GRID_PX
            y = random.randint(gy_min, gy_max) * CARGO_GRID_PX
            position = {"x": x, "y": y}
            
            if not self._check_crate_collision(position, dimensions):
                return position
        
        return None  # Couldn't find valid position

    def _area_bounds_for(self, x: int, w_px: int, h_px: int) -> Tuple[Optional[str], Tuple[int, int, int, int]]:
        """Given a tentative x, determine area ('cargoHold' or 'loadingBay') and allowed top-left bounds.
        Returns (area_name, (min_x, max_x, min_y, max_y)). If x is between areas, choose by center.
        """
        # Define areas (updated height from 200 to 180)
        hold_x, hold_y, hold_w, hold_h = 8, 60, 150, 180
        bay_x, bay_y, bay_w, bay_h = 162, 60, 150, 180
        # Decide area by x midpoint
        area_name = "cargoHold" if x < 162 else "loadingBay"
        if area_name == "cargoHold":
            min_x = hold_x
            max_x = hold_x + hold_w - w_px
            min_y = hold_y
            max_y = hold_y + hold_h - h_px
            return area_name, (min_x, max_x, min_y, max_y)
        else:
            min_x = bay_x
            max_x = bay_x + bay_w - w_px
            min_y = bay_y
            max_y = bay_y + bay_h - h_px
            return area_name, (min_x, max_x, min_y, max_y)

    def _has_corner_support(self, x: int, y: int, w_px: int, h_px: int) -> bool:
        """Return True if both bottom corners at (x, y+h) and (x+w, y+h) are supported by crate tops."""
        cargo = self.game_state.get("cargo", {})
        bottom_y = y + h_px
        left_corner_x = x
        right_corner_x = x + w_px
        supported_left = False
        supported_right = False
        for area_name in ["cargoHold", "loadingBay"]:
            for crate in cargo.get(area_name, []):
                pos = crate.get("position", {})
                cx, cy = pos.get("x", 0), pos.get("y", 0)
                ctype = crate.get("type", "")
                info = cargo.get("crateTypes", {}).get(ctype, {})
                dims = info.get("dimensions", {"width": 1, "height": 1})
                cw = max(1, dims.get("width", 1)) * CARGO_GRID_PX
                ch = max(1, dims.get("height", 1)) * CARGO_GRID_PX
                # top edge of this crate
                top_y = cy
                # Only support if top is exactly at our bottom
                if top_y == bottom_y:
                    if cx <= left_corner_x <= cx + cw:
                        supported_left = True
                    if cx <= right_corner_x <= cx + cw:
                        supported_right = True
                if supported_left and supported_right:
                    return True
        return supported_left and supported_right
    
    def _update_cargo_physics(self):
        """Update cargo weight and center of gravity calculations"""
        cargo = self.game_state.get("cargo", {})
        
        total_weight = 0.0
        weighted_x = 0.0
        weighted_y = 0.0
        
        # Only cargo hold items affect ship performance
        for crate in cargo.get("cargoHold", []):
            crate_type = crate.get("type", "")
            crate_info = cargo.get("crateTypes", {}).get(crate_type, {})
            weight = crate_info.get("weight", 0.0)
            
            position = crate.get("position", {})
            x, y = position.get("x", 0), position.get("y", 0)
            
            total_weight += weight
            weighted_x += x * weight
            weighted_y += y * weight
        
        if total_weight > 0:
            cargo["centerOfGravity"] = {
                "x": weighted_x / total_weight,
                "y": weighted_y / total_weight
            }
        else:
            cargo["centerOfGravity"] = {"x": 156.2, "y": 100.0}
        
        cargo["totalWeight"] = total_weight
    
    def add_fuel_to_tanks(self, gallons: float):
        """Add fuel to tanks (aft first, then forward)"""
        fuel = self.game_state.get("fuel", {})
        tanks = fuel.get("tanks", {})
        
        # Fill aft tank first
        aft_tank = tanks.get("aft", {})
        aft_capacity = aft_tank.get("capacity", 180.0)
        aft_current = aft_tank.get("level", 0.0)
        aft_space = aft_capacity - aft_current
        
        if gallons <= aft_space:
            # All fuel goes to aft tank
            aft_tank["level"] = aft_current + gallons
        else:
            # Fill aft tank, remainder to forward
            aft_tank["level"] = aft_capacity
            remainder = gallons - aft_space
            
            # Fill forward tank
            fwd_tank = tanks.get("forward", {})
            fwd_capacity = fwd_tank.get("capacity", 180.0)
            fwd_current = fwd_tank.get("level", 0.0)
            fwd_space = fwd_capacity - fwd_current
            
            fwd_tank["level"] = min(fwd_capacity, fwd_current + remainder)
        
        # Update total fuel level
        fuel["currentLevel"] = tanks["forward"]["level"] + tanks["aft"]["level"]

    # Settings management
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return self.game_state.get("settings", {
            "checkForUpdates": True,
            "lastUpdateCheck": 0.0,
            "updateCheckInterval": 86400.0
        })
    
    def set_setting(self, key: str, value: Any):
        """Set a specific setting value"""
        if "settings" not in self.game_state:
            self.game_state["settings"] = {
                "checkForUpdates": True,
                "lastUpdateCheck": 0.0,
                "updateCheckInterval": 86400.0
            }
        self.game_state["settings"][key] = value
    
    def should_check_for_updates(self) -> bool:
        """Check if we should check for updates based on settings and time"""
        settings = self.get_settings()
        if not settings.get("checkForUpdates", True):
            return False
        
        current_time = time.time()
        last_check = settings.get("lastUpdateCheck", 0.0)
        interval = settings.get("updateCheckInterval", 86400.0)
        
        return (current_time - last_check) >= interval
    
    def mark_update_check_completed(self):
        """Mark that an update check was just completed"""
        self.set_setting("lastUpdateCheck", time.time())

    # === WAYPOINT MANAGEMENT METHODS ===
    
    def set_waypoint(self, latitude: float, longitude: float):
        """Set a single waypoint for route following"""
        route = self.game_state["navigation"]["route"]
        route["waypoints"] = [{"latitude": latitude, "longitude": longitude}]
        route["currentWaypoint"] = 0
        route["active"] = True
        
    def clear_waypoint(self):
        """Remove the current waypoint"""
        route = self.game_state["navigation"]["route"]
        route["waypoints"] = []
        route["currentWaypoint"] = 0
        route["active"] = False
        
    def get_waypoint(self) -> Optional[Dict[str, float]]:
        """Get the current waypoint if one exists"""
        route = self.game_state["navigation"]["route"]
        if route["active"] and route["waypoints"]:
            return route["waypoints"][0]
        return None
        
    def calculate_bearing_to_waypoint(self) -> Optional[float]:
        """Calculate bearing from current position to waypoint"""
        waypoint = self.get_waypoint()
        if not waypoint:
            return None
            
        pos = self.game_state["navigation"]["position"]
        
        # Convert to radians
        lat1 = math.radians(pos["latitude"])
        lon1 = math.radians(pos["longitude"])
        lat2 = math.radians(waypoint["latitude"])
        lon2 = math.radians(waypoint["longitude"])
        
        # Calculate bearing using forward azimuth formula
        dlon = lon2 - lon1
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360  # Normalize to 0-360
        
        return bearing
        
    def calculate_distance_to_waypoint(self) -> Optional[float]:
        """Calculate distance from current position to waypoint in nautical miles"""
        waypoint = self.get_waypoint()
        if not waypoint:
            return None
            
        pos = self.game_state["navigation"]["position"]
        
        # Haversine formula for great circle distance
        lat1 = math.radians(pos["latitude"])
        lon1 = math.radians(pos["longitude"])
        lat2 = math.radians(waypoint["latitude"])
        lon2 = math.radians(waypoint["longitude"])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in nautical miles
        R = 3440.065
        distance = R * c
        
        return distance

    # Library management methods
    def add_random_book_to_library(self) -> bool:
        """Add a random available book to the library"""
        # Ensure library section exists
        if "library" not in self.game_state:
            self.game_state["library"] = {"books": []}
        
        library = self.game_state["library"]
        current_books = set(library.get("books", []))
        
        # Get all available books from assets/books/*.md
        books_dir = get_assets_path("books")
        if not os.path.exists(books_dir):
            return False
        
        available_books = []
        for filename in os.listdir(books_dir):
            if filename.endswith('.md') and filename not in current_books:
                available_books.append(filename)
        
        if not available_books:
            return False  # No new books available
        
        # Select a random book and add it to the library
        selected_book = random.choice(available_books)
        library["books"].append(selected_book)
        return True
    
    
    def remove_book_from_library(self, book_filename: str) -> bool:
        """Remove a book from the library and attach a book crate to winch (if winch is free)"""
        # Ensure library section exists
        if "library" not in self.game_state:
            self.game_state["library"] = {"books": []}
        
        library = self.game_state["library"]
        books = library.get("books", [])
        
        if book_filename not in books:
            return False
        
        # Check if winch is already busy
        cargo = self.game_state.get("cargo", {})
        winch = cargo.get("winch", {})
        if winch.get("attachedCrate"):
            # Winch is busy - cannot move book to cargo
            return False
        
        # Remove the book from library
        books.remove(book_filename)
        
        # Create a book crate and attach it to the winch
        new_crate = self.game_state["cargo"]["crateTypes"]["books"].copy()
        new_crate["id"] = str(uuid.uuid4())
        new_crate["type"] = "books"
        new_crate["position"] = {"x": 0, "y": 0}  # Position doesn't matter when attached to winch

        # Attach the crate to the winch (attached crates don't exist in cargoHold or loadingBay)
        winch["attachedCrate"] = new_crate["id"]
        
        # Set winch position to center and extend cable slightly so it's visible
        winch["position"] = {"x": 160, "y": 50}
        winch["cableLength"] = max(20, winch.get("cableLength", 0))  # Ensure some cable is extended
        
        # Store the attached crate data in a special field for attached crates
        cargo.setdefault("attachedCrateData", {})[new_crate["id"]] = new_crate
        
        self._update_cargo_physics()
        return True

    # Bookmark management methods
    def set_bookmark(self, book_filename: str, page_number: int):
        """Set a bookmark for a specific book"""
        # Ensure library section exists
        if "library" not in self.game_state:
            self.game_state["library"] = {"books": [], "bookmarks": {}}
        
        library = self.game_state["library"]
        if "bookmarks" not in library:
            library["bookmarks"] = {}
        
        library["bookmarks"][book_filename] = page_number

    def get_bookmark(self, book_filename: str) -> Optional[int]:
        """Get the bookmark page number for a specific book"""
        # Ensure library section exists
        if "library" not in self.game_state:
            self.game_state["library"] = {"books": [], "bookmarks": {}}
        
        library = self.game_state["library"]
        if "bookmarks" not in library:
            library["bookmarks"] = {}
        
        return library["bookmarks"].get(book_filename)

    def remove_bookmark(self, book_filename: str):
        """Remove the bookmark for a specific book"""
        # Ensure library section exists
        if "library" not in self.game_state:
            self.game_state["library"] = {"books": [], "bookmarks": {}}
        
        library = self.game_state["library"]
        if "bookmarks" not in library:
            library["bookmarks"] = {}
        
        if book_filename in library["bookmarks"]:
            del library["bookmarks"][book_filename]

    def has_bookmark(self, book_filename: str) -> bool:
        """Check if a book has a bookmark"""
        return self.get_bookmark(book_filename) is not None


# Global simulator instance
_simulator = None

def get_simulator(custom_save_path: Optional[str] = None) -> CoreSimulator:
    """Get the global simulator instance, optionally with custom save path"""
    global _simulator
    if _simulator is None:
        _simulator = CoreSimulator(custom_save_path)
    return _simulator
