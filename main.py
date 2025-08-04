"""
Main Application for Airship Zero
Brutally simple scene management with 320x320 rendering
"""
import pygame
import sys
import os
from typing import Dict, Any, Optional

# Import scenes
from scene_main_menu import MainMenuScene
from scene_bridge import BridgeScene
from scene_engine_room import EngineRoomScene

# Constants
LOGICAL_SIZE = 320
MIN_WINDOW_SIZE = 640
DEFAULT_WINDOW_SIZE = 960

class AirshipApp:
    def __init__(self):
        pygame.init()
        
        # Initialize window
        self.window_size = (DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_SIZE)
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        pygame.display.set_caption("Airship Zero")
        
        # Create logical rendering surface
        self.logical_surface = pygame.Surface((LOGICAL_SIZE, LOGICAL_SIZE))
        
        # Load font
        self.font = self._load_font()
        
        # Initialize game state
        self.game_state = self._create_initial_game_state()
        
        # Scene management
        self.current_scene = None
        self.scene_name = "scene_main_menu"
        self.scenes = {}
        self.running = True
        
        # Initialize scenes
        self._init_scenes()
        
        # Game clock
        self.clock = pygame.time.Clock()
        
    def _load_font(self):
        """Load the Pixelify Sans font or fallback"""
        try:
            # Try to load Pixelify Sans from our assets
            pixelify_paths = [
                "assets/fonts/Pixelify_Sans/static/PixelifySans-Regular.ttf",
                "assets/fonts/Pixelify_Sans/PixelifySans-VariableFont_wght.ttf",
            ]
            
            for path in pixelify_paths:
                if os.path.exists(path):
                    print(f"✅ Loading Pixelify Sans from: {path}")
                    return pygame.font.Font(path, 10)
                    
            # Fallback - should not happen if fonts are properly installed
            print("⚠️  Pixelify Sans not found, using fallback")
            return pygame.font.Font(None, 12)
                
        except Exception as e:
            print(f"❌ Font loading error: {e}")
            # Ultimate fallback
            return pygame.font.Font(None, 12)
            
    def _create_initial_game_state(self) -> Dict[str, Any]:
        """Create the initial game state"""
        return {
            "navigation": {
                "currentAltitude": 1250.0,
                "targetAltitude": 1250.0,
                "indicatedAirspeed": 85.0,
                "currentHeading": 45.0,
                "targetHeading": 45.0,
                "pitch": 0.0,
                "roll": 0.0,
                "verticalSpeed": 0.0,
                "mode": "manual",
                "autopilot": {
                    "engaged": False,
                    "headingHold": False,
                    "altitudeHold": False
                }
            },
            "engine": {
                "running": True,
                "rpm": 2650.0,
                "manifoldPressure": 24.5,
                "fuelFlow": 12.8,
                "oilPressure": 65.0,
                "oilTemperature": 185.0,
                "cylinderHeadTemp": 320.0,
                "exhaustGasTemp": 1450.0,
                "fuelPressure": 22.0,
                "throttlePosition": 0.75,
                "mixturePosition": 0.85,
                "propellerPosition": 0.80,
                "propellerFeathered": False,
                "emergencyShutdown": False
            },
            "electrical": {
                "batteryBusA": {
                    "switch": True,
                    "voltage": 12.6,
                    "current": 8.5
                },
                "batteryBusB": {
                    "switch": True,
                    "voltage": 12.5,
                    "current": 6.2
                },
                "alternator": {
                    "online": True,
                    "voltage": 14.2,
                    "current": 15.0
                }
            },
            "fuel": {
                "totalCapacity": 550.0,
                "currentLevel": 425.0,
                "pumpMode": "auto",
                "tanks": {
                    "forward": {"level": 140.0, "capacity": 180.0},
                    "center": {"level": 145.0, "capacity": 190.0}, 
                    "aft": {"level": 140.0, "capacity": 180.0}
                }
            },
            "time": {
                "totalFlightTime": 0.0,
                "sessionTime": 0.0
            }
        }
        
    def _init_scenes(self):
        """Initialize all scenes"""
        self.scenes["scene_main_menu"] = MainMenuScene()
        self.scenes["scene_bridge"] = BridgeScene(self.game_state)
        self.scenes["scene_engine_room"] = EngineRoomScene(self.game_state)
        
        # Set fonts for all scenes
        for scene in self.scenes.values():
            scene.set_font(self.font)
            
        # Set current scene
        self.current_scene = self.scenes[self.scene_name]
        
    def _transition_to_scene(self, scene_name: str):
        """Transition to a new scene"""
        if scene_name == "quit":
            self.running = False
            return
            
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
        
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.QUIT:
            self.running = False
            return
            
        elif event.type == pygame.VIDEORESIZE:
            # Handle window resize
            new_width = max(MIN_WINDOW_SIZE, event.w)
            new_height = max(MIN_WINDOW_SIZE, event.h)
            self.window_size = (new_width, new_height)
            self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
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
        # Update current scene
        if self.current_scene and hasattr(self.current_scene, 'update'):
            self.current_scene.update(dt)
            
        # Update game time
        if self.scene_name != "scene_main_menu":
            self.game_state["time"]["sessionTime"] += dt
            self.game_state["time"]["totalFlightTime"] += dt
            
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
        print("Starting Airship Zero...")
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
        pygame.quit()
        print("Airship Zero shutdown complete.")

def main():
    """Application entry point"""
    try:
        app = AirshipApp()
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
