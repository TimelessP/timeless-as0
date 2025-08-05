"""
Camera Scene - Photography mission interface
Handles camera controls, mission progress, and photo gallery
"""
import pygame
from typing import Optional

# Colors
BACKGROUND_COLOR = (20, 20, 30)
TEXT_COLOR = (255, 255, 255)
FOCUS_COLOR = (255, 200, 50)
BUTTON_COLOR = (60, 60, 80)
BUTTON_FOCUSED_COLOR = (80, 80, 120)
GOOD_COLOR = (100, 255, 100)
WARNING_COLOR = (255, 100, 100)
CAMERA_HEADER_COLOR = (40, 20, 60)  # Purple for camera scene

class CameraScene:
    def __init__(self, simulator):
        self.simulator = simulator
        self.font = None
        self.is_text_antialiased = False
        self.widgets = []
        self.focused_widget = 0
        
        self._init_widgets()
    
    def set_font(self, font, is_text_antialiased=False):
        """Set the font for this scene"""
        self.font = font
        self.is_text_antialiased = is_text_antialiased
    
    def _init_widgets(self):
        """Initialize camera widgets"""
        self.widgets = [
            # Navigation buttons
            {"id": "prev_scene", "type": "button", "position": [8, 290], "size": [60, 24], "text": "< [", "focused": True},
            {"id": "next_scene", "type": "button", "position": [252, 290], "size": [60, 24], "text": "] >", "focused": False},
            
            # Camera status
            {"id": "camera_status", "type": "label", "position": [8, 40], "size": [150, 16], "text": "Camera: READY", "focused": False},
            {"id": "battery_level", "type": "label", "position": [8, 60], "size": [150, 16], "text": "Battery: 78%", "focused": False},
            {"id": "storage_space", "type": "label", "position": [8, 80], "size": [150, 16], "text": "Storage: 384.7 GB", "focused": False},
            
            # Camera controls
            {"id": "take_photo", "type": "button", "position": [8, 110], "size": [80, 20], "text": "Photo", "focused": False},
            {"id": "start_recording", "type": "button", "position": [100, 110], "size": [80, 20], "text": "Record", "focused": False},
            {"id": "stop_recording", "type": "button", "position": [190, 110], "size": [80, 20], "text": "Stop", "focused": False},
            
            # Gimbal controls
            {"id": "gimbal_pitch", "type": "label", "position": [8, 140], "size": [100, 16], "text": "Pitch: -15.0°", "focused": False},
            {"id": "gimbal_yaw", "type": "label", "position": [120, 140], "size": [100, 16], "text": "Yaw: 0.0°", "focused": False},
            {"id": "gimbal_lock", "type": "button", "position": [8, 160], "size": [60, 16], "text": "Lock", "focused": False},
            
            # Mission progress
            {"id": "mission_status", "type": "label", "position": [8, 190], "size": [200, 16], "text": "Mission: Survey Progress", "focused": False},
            {"id": "photos_taken", "type": "label", "position": [8, 210], "size": [150, 16], "text": "Photos: 12/20", "focused": False},
        ]
        
        # Set initial focus
        if self.widgets:
            self.widgets[self.focused_widget]["focused"] = True
    
    def update(self, dt: float):
        """Update camera display with current simulator data"""
        if not self.simulator:
            return
            
        state = self.simulator.get_state()
        camera = state.get("camera", {})
        
        # Update camera status
        mounted = camera.get("mounted", False)
        status = "READY" if mounted else "OFFLINE"
        self.widgets[2]["text"] = f"Camera: {status}"
        
        # Update battery
        battery = camera.get("battery", {})
        level = battery.get("level", 0) * 100
        self.widgets[3]["text"] = f"Battery: {level:.0f}%"
        
        # Update storage
        storage = camera.get("storage", {})
        available = storage.get("availableSpace", 0)
        self.widgets[4]["text"] = f"Storage: {available:.1f} GB"
        
        # Update gimbal
        gimbal = camera.get("gimbal", {})
        pitch = gimbal.get("pitch", 0)
        yaw = gimbal.get("yaw", 0)
        locked = gimbal.get("locked", False)
        self.widgets[8]["text"] = f"Pitch: {pitch:.1f}°"
        self.widgets[9]["text"] = f"Yaw: {yaw:.1f}°"
        self.widgets[10]["text"] = "Unlock" if locked else "Lock"
        
        # Update mission progress
        session = camera.get("session", {})
        recording = session.get("recording", False)
        if recording:
            self.widgets[6]["text"] = "Recording..."
        
        # Update mission info (stub data)
        self.widgets[11]["text"] = "Mission: Photo Survey"
        self.widgets[12]["text"] = "Photos: 12/20"
    
    def handle_event(self, event) -> Optional[str]:
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "scene_main_menu"
            elif event.key == pygame.K_LEFTBRACKET:  # [
                return self._get_prev_scene()
            elif event.key == pygame.K_RIGHTBRACKET:  # ]
                return self._get_next_scene()
            elif event.key == pygame.K_TAB:
                if event.mod & pygame.KMOD_SHIFT:
                    self._cycle_focus(-1)
                else:
                    self._cycle_focus(1)
            elif event.key == pygame.K_RETURN:
                return self._activate_focused()
            elif event.key == pygame.K_SPACE:
                # Quick photo shortcut
                self._take_photo()
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                clicked_widget = self._get_widget_at_pos(event.pos)
                if clicked_widget is not None:
                    self._set_focus(clicked_widget)
                    return self._activate_focused()
        
        return None
    
    def _get_prev_scene(self) -> str:
        """Get the previous scene in circular order"""
        return "scene_communications"
    
    def _get_next_scene(self) -> str:
        """Get the next scene in circular order"""
        return "scene_crew"
    
    def _take_photo(self):
        """Take a photo (stub implementation)"""
        # TODO: Implement actual photo taking logic
        pass
    
    def _get_widget_at_pos(self, pos):
        """Find widget at given position"""
        x, y = pos
        for i, widget in enumerate(self.widgets):
            wx, wy = widget["position"]
            ww, wh = widget["size"]
            if wx <= x <= wx + ww and wy <= y <= wy + wh:
                return i
        return None
    
    def _set_focus(self, widget_index):
        """Set focus to specific widget"""
        # Clear current focus
        for widget in self.widgets:
            widget["focused"] = False
        
        # Set new focus
        if 0 <= widget_index < len(self.widgets):
            self.focused_widget = widget_index
            self.widgets[widget_index]["focused"] = True
    
    def _cycle_focus(self, direction):
        """Cycle focus through widgets"""
        if not self.widgets:
            return
            
        self.widgets[self.focused_widget]["focused"] = False
        self.focused_widget = (self.focused_widget + direction) % len(self.widgets)
        self.widgets[self.focused_widget]["focused"] = True
    
    def _activate_focused(self) -> Optional[str]:
        """Activate the currently focused widget"""
        if not self.widgets:
            return None
            
        widget = self.widgets[self.focused_widget]
        widget_id = widget["id"]
        
        if widget_id == "prev_scene":
            return self._get_prev_scene()
        elif widget_id == "next_scene":
            return self._get_next_scene()
        elif widget_id == "take_photo":
            self._take_photo()
        elif widget_id == "start_recording":
            # TODO: Start recording
            pass
        elif widget_id == "stop_recording":
            # TODO: Stop recording
            pass
        elif widget_id == "gimbal_lock":
            # TODO: Toggle gimbal lock
            pass
            
        return None
    
    def render(self, surface):
        """Render the camera scene"""
        # Clear background
        surface.fill(BACKGROUND_COLOR)
        
        if not self.font:
            return
        
        # Draw colored title header
        pygame.draw.rect(surface, CAMERA_HEADER_COLOR, (0, 0, 320, 24))
        pygame.draw.rect(surface, TEXT_COLOR, (0, 0, 320, 24), 1)
        
        # Centered title
        title = self.font.render("CAMERA SYSTEM", self.is_text_antialiased, TEXT_COLOR)
        title_x = (320 - title.get_width()) // 2
        surface.blit(title, (title_x, 4))
        
        # Render widgets
        for widget in self.widgets:
            self._render_widget(surface, widget)
    
    def _render_widget(self, surface, widget):
        """Render a single widget"""
        if not self.font:
            return
            
        x, y = widget["position"]
        w, h = widget["size"]
        focused = widget["focused"]
        widget_type = widget["type"]
        text = widget["text"]
        
        if widget_type == "button":
            # Draw button background
            color = BUTTON_FOCUSED_COLOR if focused else BUTTON_COLOR
            pygame.draw.rect(surface, color, (x, y, w, h))
            pygame.draw.rect(surface, TEXT_COLOR, (x, y, w, h), 1)
            
            # Draw button text
            text_color = FOCUS_COLOR if focused else TEXT_COLOR
            text_surface = self.font.render(text, self.is_text_antialiased, text_color)
            text_x = x + (w - text_surface.get_width()) // 2
            text_y = y + (h - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
            
        elif widget_type == "label":
            # Draw label text
            text_color = FOCUS_COLOR if focused else TEXT_COLOR
            text_surface = self.font.render(text, self.is_text_antialiased, text_color)
            surface.blit(text_surface, (x, y))
