"""
Main Application for Airship Zero
Brutally simple scene management with 320x320 rendering
"""
import pygame
import sys
import os
import argparse
import tomllib
from typing import Dict, Any, Optional

# Import scenes
from scene_main_menu import MainMenuScene
from scene_bridge import BridgeScene
from scene_engine_room import EngineRoomScene
from scene_navigation import NavigationScene
from scene_fuel import FuelScene
from scene_cargo import CargoScene
from scene_communications import CommunicationsScene
from scene_camera import CameraScene
from scene_crew import CrewScene
from scene_missions import MissionsScene
from scene_update import SceneUpdate
from core_simulator import get_simulator

# Constants
LOGICAL_SIZE = 320
MIN_WINDOW_SIZE = 640
DEFAULT_WINDOW_SIZE = 960
FULLSCREEN_RESOLUTION = (1920, 1080)
DEFAULT_FONT_SIZE = 13

# Global assets directory (set by main app)
_assets_dir = None

def get_assets_dir() -> str:
    """Get the assets directory path for use by any module"""
    global _assets_dir
    if _assets_dir is None:
        # Fallback detection if not set by main app
        if os.path.exists("assets"):
            _assets_dir = "assets"
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            _assets_dir = os.path.join(script_dir, "assets")
    return _assets_dir

def set_assets_dir(path: str):
    """Set the assets directory path (called by main app)"""
    global _assets_dir
    _assets_dir = path

def get_version() -> str:
    """Get version from pyproject.toml"""
    try:
        # Look for pyproject.toml relative to this script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        toml_path = os.path.join(script_dir, "pyproject.toml")
        
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    except Exception:
        return "unknown"

class AirshipApp:
    def __init__(self, save_file_path: Optional[str] = None):
        pygame.init()
        
        # Store custom save file path for the simulator
        self.save_file_path = save_file_path
        
        # Determine asset directory location
        self.assets_dir = self._find_assets_dir()
        
        # Set global assets directory for other modules
        set_assets_dir(self.assets_dir)
        
        # Text rendering configuration
        self.is_text_antialiased = True
        
        # Fullscreen state
        self.is_fullscreen = False
        self.windowed_size = (DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_SIZE)
        
        # Initialize window
        self.window_size = self.windowed_size
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        pygame.display.set_caption("Airship Zero")
        
        # Create logical rendering surface
        self.logical_surface = pygame.Surface((LOGICAL_SIZE, LOGICAL_SIZE))
        
        # Load font
        self.font = self._load_font()
        
        # Get the centralized simulator with custom save path if provided
        self.simulator = get_simulator(self.save_file_path)
        
        # Scene management
        self.current_scene = None
        self.scene_name = "scene_main_menu"
        self.scenes = {}
        self.running = True
        
        # Initialize scenes
        self._init_scenes()
        
        # Check for updates if enabled
        self._check_for_updates_if_needed()
        
        # Game clock
        self.clock = pygame.time.Clock()
        
    def _find_assets_dir(self) -> str:
        """Find the assets directory relative to the package location"""
        # Try relative path first (development mode)
        if os.path.exists("assets"):
            return "assets"
        
        # Try relative to this script (package mode)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(script_dir, "assets")
        if os.path.exists(assets_path):
            return assets_path
            
        # Last resort: try relative to the main module
        try:
            import __main__
            if hasattr(__main__, '__file__'):
                main_dir = os.path.dirname(os.path.abspath(__main__.__file__))
                assets_path = os.path.join(main_dir, "assets")
                if os.path.exists(assets_path):
                    return assets_path
        except:
            pass
            
        # If all else fails, return relative path and hope for the best
        return "assets"
        
    def _load_font(self):
        """Load the font or fallback"""
        try:
            # Use the dynamically found assets directory
            font_path = os.path.join(self.assets_dir, "fonts", "Roboto_Condensed", "RobotoCondensed-VariableFont_wght.ttf")
            
            if os.path.exists(font_path):
                print(f"✅ Loading font from: {font_path}")
                return pygame.font.Font(font_path, DEFAULT_FONT_SIZE)
                    
            # Fallback - should not happen if fonts are properly installed
            print(f"⚠️  Font not found at {font_path}, using fallback")
            print(f"    Assets directory: {self.assets_dir}")
            return pygame.font.Font(None, DEFAULT_FONT_SIZE)
                
        except Exception as e:
            print(f"❌ Font loading error: {e}")
            # Ultimate fallback
            return pygame.font.Font(None, DEFAULT_FONT_SIZE)
            
    def _init_scenes(self):
        """Initialize all scenes"""
        self.scenes["scene_main_menu"] = MainMenuScene()
        self.scenes["scene_bridge"] = BridgeScene(self.simulator)
        self.scenes["scene_engine_room"] = EngineRoomScene(self.simulator)
        self.scenes["scene_navigation"] = NavigationScene(self.simulator)
        self.scenes["scene_fuel"] = FuelScene(self.simulator)
        self.scenes["scene_cargo"] = CargoScene(self.simulator)
        self.scenes["scene_communications"] = CommunicationsScene(self.simulator)
        self.scenes["scene_camera"] = CameraScene(self.simulator)
        self.scenes["scene_crew"] = CrewScene(self.simulator)
        self.scenes["scene_missions"] = MissionsScene(self.simulator)
        self.scenes["scene_update"] = SceneUpdate(self.font)
        
        # Set up cross-references
        self.scenes["scene_update"].set_main_menu_scene(self.scenes["scene_main_menu"])
        
        # Set fonts for all scenes
        for scene in self.scenes.values():
            scene.set_font(self.font, self.is_text_antialiased)
            
        # Set current scene
        self.current_scene = self.scenes[self.scene_name]
        
        # Check for existing saved game and enable resume button
        if self.simulator.has_saved_game():
            self.scenes["scene_main_menu"].set_game_exists(True)
    
    def _check_for_updates_if_needed(self):
        """Check for updates if settings allow and enough time has passed"""
        try:
            if self.simulator.should_check_for_updates():
                # Delegate to the update scene to perform the check
                update_scene = self.scenes.get("scene_update")
                if update_scene:
                    # Trigger automatic check (CDN-friendly, no force_fresh)
                    update_scene._check_latest_version(force_fresh=False)
        except Exception as e:
            print(f"Error during automatic update check: {e}")
        
    def _transition_to_scene(self, scene_name: str):
        """Transition to a new scene"""
        if scene_name == "quit":
            self.running = False
            return
        elif scene_name == "new_game":
            # Start a new game
            self.simulator.start_new_game()
            scene_name = "scene_bridge"
        elif scene_name == "resume_game":
            # Load saved game
            if self.simulator.load_game():
                scene_name = "scene_bridge"
            else:
                # Failed to load, stay on main menu
                return
        elif scene_name == "scene_main_menu":
            # Save game when returning to main menu
            if self.simulator.running:
                self.simulator.save_game()
                
        if scene_name in self.scenes:
            self.scene_name = scene_name
            self.current_scene = self.scenes[scene_name]
            
            # Enable resume game button if we've started a game
            if scene_name != "scene_main_menu":
                self.scenes["scene_main_menu"].set_game_exists(True)
                
    def _screen_to_logical(self, screen_pos) -> tuple:
        """Convert screen coordinates to logical coordinates"""
        screen_w, screen_h = self.window_size
        scale = min(screen_w / LOGICAL_SIZE, screen_h / LOGICAL_SIZE)
        
        # Calculate the actual rendered size and position
        rendered_size = int(LOGICAL_SIZE * scale)
        offset_x = (screen_w - rendered_size) // 2
        offset_y = (screen_h - rendered_size) // 2
        
        # Convert screen coordinates to logical coordinates
        screen_x, screen_y = screen_pos
        logical_x = (screen_x - offset_x) / scale
        logical_y = (screen_y - offset_y) / scale
        
        # Clamp to logical bounds
        logical_x = max(0, min(LOGICAL_SIZE - 1, logical_x))
        logical_y = max(0, min(LOGICAL_SIZE - 1, logical_y))
        
        return (int(logical_x), int(logical_y))
        
    def _toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        if self.is_fullscreen:
            # Switch to windowed mode
            self.is_fullscreen = False
            self.window_size = self.windowed_size
            self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
            print(f"Switched to windowed mode: {self.window_size[0]}x{self.window_size[1]}")
        else:
            # Store current windowed size
            if not self.is_fullscreen:
                self.windowed_size = self.window_size
            # Switch to fullscreen mode
            self.is_fullscreen = True
            self.window_size = FULLSCREEN_RESOLUTION
            self.screen = pygame.display.set_mode(self.window_size, pygame.FULLSCREEN)
            print(f"Switched to fullscreen mode: {self.window_size[0]}x{self.window_size[1]}")
        
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.QUIT:
            self.running = False
            return
            
        elif event.type == pygame.KEYDOWN:
            # Handle global key events
            if event.key == pygame.K_F11:
                self._toggle_fullscreen()
                return
            
        elif event.type == pygame.VIDEORESIZE:
            # Handle window resize (only in windowed mode)
            if not self.is_fullscreen:
                new_width = max(MIN_WINDOW_SIZE, event.w)
                new_height = max(MIN_WINDOW_SIZE, event.h)
                self.window_size = (new_width, new_height)
                self.windowed_size = self.window_size
            # Every AI seems to do this but it's not correct to do so,
            # because it destroys and re-creates the window.
            # self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
            return
            
        # Convert mouse events to logical coordinates
        if hasattr(event, 'pos'):
            event.pos = self._screen_to_logical(event.pos)
            
        # Pass event to current scene
        if self.current_scene:
            result = self.current_scene.handle_event(event)
            if result:
                self._transition_to_scene(result)
                
    def update(self, dt: float):
        """Update the game state"""
        # Update the centralized simulator
        self.simulator.update(dt)
        
        # Update current scene
        if self.current_scene and hasattr(self.current_scene, 'update'):
            self.current_scene.update(dt)
            
    def render(self):
        """Render the current frame"""
        # Clear the logical surface
        self.logical_surface.fill((0, 0, 0))
        
        # Render current scene to logical surface
        if self.current_scene:
            self.current_scene.render(self.logical_surface)
            
        # Scale and center on screen
        screen_w, screen_h = self.window_size
        scale = min(screen_w / LOGICAL_SIZE, screen_h / LOGICAL_SIZE)
        
        # Calculate rendered size and position
        rendered_size = int(LOGICAL_SIZE * scale)
        offset_x = (screen_w - rendered_size) // 2
        offset_y = (screen_h - rendered_size) // 2
        
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Scale logical surface to screen
        if scale != 1.0:
            scaled_surface = pygame.transform.scale(
                self.logical_surface, 
                (rendered_size, rendered_size)
            )
        else:
            scaled_surface = self.logical_surface
            
        # Blit to screen
        self.screen.blit(scaled_surface, (offset_x, offset_y))
        
        # Update display
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        version = get_version()
        print(f"Starting Airship Zero v{version}...")
        print(f"Logical resolution: {LOGICAL_SIZE}x{LOGICAL_SIZE}")
        print(f"Window size: {self.window_size[0]}x{self.window_size[1]}")
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(60) / 1000.0  # Convert to seconds
            
            # Handle events
            for event in pygame.event.get():
                self.handle_event(event)
                
            # Update game state
            self.update(dt)
            
            # Render frame
            self.render()
            
        # Cleanup
        # Auto-save game state on exit if game is running
        if self.simulator.running:
            print("Auto-saving game state...")
            self.simulator.save_game()
        
        pygame.quit()
        print("Airship Zero shutdown complete.")

def main():
    """Application entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Airship Zero - Retro airship simulation game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Use default save location
  %(prog)s --save-file custom_game.json      # Use custom file in current directory
  %(prog)s --save-file /path/to/game.json    # Use absolute path
        """
    )
    parser.add_argument(
        '--save-file', '--save', '-s',
        metavar='PATH',
        help='Custom path for the save file (default: OS-appropriate app data directory)'
    )
    
    args = parser.parse_args()
    
    try:
        app = AirshipApp(save_file_path=args.save_file)
        app.run()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
