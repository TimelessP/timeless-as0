"""
Update Scene for Airship Zero
Version checking and automatic update functionality
"""
import os
import pygame
import subprocess
import sys
import time
from typing import Optional, Dict, Any
from core_simulator import get_simulator

try:
    import urllib.request
    import urllib.error
    import tomllib
except ImportError:
    # Fallback for older Python versions
    urllib = None
    tomllib = None

# UI Constants (matching main menu style)
BACKGROUND_COLOR = (20, 20, 30)
TEXT_COLOR = (255, 255, 255)
FOCUS_COLOR = (255, 200, 50)
BUTTON_COLOR = (60, 60, 80)
BUTTON_FOCUSED_COLOR = (80, 80, 120)
WARNING_COLOR = (255, 100, 100)
CAUTION_COLOR = (255, 200, 100)
GOOD_COLOR = (100, 255, 100)

class SceneUpdate:
    def __init__(self, font):
        self.font = font
        self.is_text_antialiased = True
        self.simulator = get_simulator()
        self.widgets = []
        self.focused_widget_index = 0
        self.main_menu_scene = None  # Will be set by main app
        
        self.current_version = None
        self.latest_version = None
        self.update_available = False
        self.checking_version = False
        self.update_status = ""
        self.updating = False
        
        self._init_widgets()
        self._check_current_version()
    
    def set_main_menu_scene(self, main_menu_scene):
        """Set reference to main menu scene for notifications"""
        self.main_menu_scene = main_menu_scene
    
    def _init_widgets(self):
        """Initialize UI widgets"""
        self.widgets = [
            {
                "id": "check_now",
                "type": "button",
                "position": [80, 120],
                "size": [160, 24],
                "text": "Check for Updates",
                "focused": True,
                "enabled": True
            },
            {
                "id": "update_now",
                "type": "button", 
                "position": [80, 150],
                "size": [160, 24],
                "text": "Download and Update",
                "focused": False,
                "enabled": False
            },
            {
                "id": "remind_later",
                "type": "button",
                "position": [80, 180],
                "size": [160, 24], 
                "text": "Remind Me Later",
                "focused": False,
                "enabled": False
            },
            {
                "id": "disable_updates",
                "type": "button",
                "position": [80, 210],
                "size": [160, 24],
                "text": "Don't Check for Updates",
                "focused": False,
                "enabled": True
            },
            {
                "id": "back",
                "type": "button",
                "position": [80, 250],
                "size": [160, 24],
                "text": "Back to Main Menu",
                "focused": False,
                "enabled": True
            }
        ]
    
    def _check_current_version(self):
        """Get the current version from pyproject.toml"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            pyproject_path = os.path.join(script_dir, "pyproject.toml")
            
            if os.path.exists(pyproject_path):
                with open(pyproject_path, "rb") as f:
                    if tomllib:
                        data = tomllib.load(f)
                        self.current_version = data.get("project", {}).get("version", "unknown")
                    else:
                        # Fallback parsing for older Python
                        content = f.read().decode('utf-8')
                        for line in content.split('\n'):
                            if 'version =' in line:
                                self.current_version = line.split('"')[1]
                                break
            else:
                self.current_version = "unknown"
        except Exception as e:
            print(f"Error reading version: {e}")
            self.current_version = "unknown"
    
    def _check_latest_version(self):
        """Check the latest version from GitHub"""
        if self.checking_version:
            return
        
        self.checking_version = True
        self.update_status = "Checking for updates..."
        
        try:
            # GitHub raw file URL for main branch
            url = "https://raw.githubusercontent.com/TimelessP/timeless-as0/main/pyproject.toml"
            
            if urllib.request:
                with urllib.request.urlopen(url, timeout=10) as response:
                    content = response.read().decode('utf-8')
            else:
                # Fallback - this shouldn't happen on modern Python
                self.update_status = "Update checking not supported on this Python version"
                return
                
            if tomllib:
                # Parse TOML properly
                data = tomllib.loads(content)
                self.latest_version = data.get("project", {}).get("version", "unknown")
            else:
                # Fallback parsing
                for line in content.split('\n'):
                    if 'version =' in line:
                        self.latest_version = line.split('"')[1]
                        break
            
            # Compare versions
            if self.latest_version and self.current_version:
                version_diff = self._version_compare(self.latest_version, self.current_version)
                if version_diff > 0:
                    self.update_available = True
                    self.update_status = f"Update available: v{self.latest_version}"
                    # Enable update buttons
                    for widget in self.widgets:
                        if widget["id"] in ["update_now", "remind_later"]:
                            widget["enabled"] = True
                    # Notify main menu
                    if self.main_menu_scene:
                        self.main_menu_scene.set_update_available(True, self.latest_version)
                elif version_diff < 0:
                    self.update_available = False
                    self.update_status = f"Development version (v{self.current_version}) - newer than released (v{self.latest_version})"
                    # Notify main menu (no update available)
                    if self.main_menu_scene:
                        self.main_menu_scene.set_update_available(False)
                else:
                    self.update_available = False
                    self.update_status = "You have the latest version"
                    # Notify main menu
                    if self.main_menu_scene:
                        self.main_menu_scene.set_update_available(False)
            else:
                self.update_status = "Could not determine versions"
                
        except urllib.error.URLError as e:
            self.update_status = f"Network error: {str(e)}"
        except Exception as e:
            self.update_status = f"Error checking updates: {str(e)}"
        finally:
            self.checking_version = False
            # Mark that we completed an update check
            self.simulator.mark_update_check_completed()
    
    def _version_compare(self, version1: str, version2: str) -> int:
        """Compare two version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal"""
        def version_parts(v):
            try:
                return [int(x) for x in v.split('.')]
            except:
                return [0, 0, 0]
        
        v1_parts = version_parts(version1)
        v2_parts = version_parts(version2)
        
        # Pad to same length
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))
        
        for i in range(max_len):
            if v1_parts[i] > v2_parts[i]:
                return 1
            elif v1_parts[i] < v2_parts[i]:
                return -1
        return 0
    
    def _perform_update(self):
        """Perform the actual update using UV tool"""
        if self.updating:
            return
        
        self.updating = True
        self.update_status = "Updating... please wait"
        
        try:
            # Use UV to update the tool
            result = subprocess.run([
                "uv", "tool", "upgrade", "airshipzero"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.update_status = "Update complete! Please restart the application"
                # Wait a moment then exit
                time.sleep(2)
                return "quit"
            else:
                self.update_status = f"Update failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            self.update_status = "Update timed out"
        except Exception as e:
            self.update_status = f"Update error: {str(e)}"
        finally:
            self.updating = False
    
    def _set_focus(self, widget_index: int):
        """Set focus to a specific widget"""
        if 0 <= widget_index < len(self.widgets):
            for i, widget in enumerate(self.widgets):
                widget["focused"] = (i == widget_index)
            self.focused_widget_index = widget_index
    
    def _get_widget_at_pos(self, pos) -> Optional[int]:
        """Get widget index at position, or None if no widget"""
        x, y = pos
        for i, widget in enumerate(self.widgets):
            if not widget.get("enabled", True):
                continue
            wx, wy = widget["position"]
            ww, wh = widget["size"]
            if wx <= x <= wx + ww and wy <= y <= wy + wh:
                return i
        return None
    
    def _activate_focused(self) -> Optional[str]:
        """Activate the currently focused widget"""
        if 0 <= self.focused_widget_index < len(self.widgets):
            widget = self.widgets[self.focused_widget_index]
            if not widget.get("enabled", True):
                return None
                
            widget_id = widget["id"]
            
            if widget_id == "check_now":
                self._check_latest_version()
            elif widget_id == "update_now":
                if self.update_available:
                    return self._perform_update()
            elif widget_id == "remind_later":
                # Reset the last check time so we'll check again later
                self.simulator.set_setting("lastUpdateCheck", time.time() - 82800)  # 23 hours ago
                return "scene_main_menu"
            elif widget_id == "disable_updates":
                self.simulator.set_setting("checkForUpdates", False)
                return "scene_main_menu"
            elif widget_id == "back":
                return "scene_main_menu"
        
        return None
    
    def handle_event(self, event) -> Optional[str]:
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "scene_main_menu"
            elif event.key == pygame.K_TAB:
                # Cycle focus
                enabled_widgets = [i for i, w in enumerate(self.widgets) if w.get("enabled", True)]
                if enabled_widgets:
                    if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]:
                        # Reverse direction
                        try:
                            current_pos = enabled_widgets.index(self.focused_widget_index)
                            new_pos = (current_pos - 1) % len(enabled_widgets)
                        except ValueError:
                            new_pos = len(enabled_widgets) - 1
                    else:
                        # Forward direction
                        try:
                            current_pos = enabled_widgets.index(self.focused_widget_index)
                            new_pos = (current_pos + 1) % len(enabled_widgets)
                        except ValueError:
                            new_pos = 0
                    self._set_focus(enabled_widgets[new_pos])
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._activate_focused()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                clicked_widget = self._get_widget_at_pos(event.pos)
                if clicked_widget is not None:
                    self._set_focus(clicked_widget)
                    return self._activate_focused()
        
        return None
    
    def update(self, dt: float):
        """Update scene state"""
        pass
    
    def set_font(self, font, is_antialiased: bool):
        """Set the font for this scene"""
        self.font = font
        self.is_text_antialiased = is_antialiased
    
    def _render_widget(self, surface, widget):
        """Render a single widget"""
        x, y = widget["position"]
        w, h = widget["size"]
        enabled = widget.get("enabled", True)
        
        if widget["type"] == "button":
            # Choose colors based on state
            if enabled:
                bg_color = BUTTON_FOCUSED_COLOR if widget["focused"] else BUTTON_COLOR
                text_color = FOCUS_COLOR if widget["focused"] else TEXT_COLOR
            else:
                bg_color = (40, 40, 50)  # Darker for disabled
                text_color = (120, 120, 120)  # Greyed out
            
            # Draw button background
            pygame.draw.rect(surface, bg_color, (x, y, w, h))
            pygame.draw.rect(surface, text_color, (x, y, w, h), 1)
            
            # Render text
            text_surface = self.font.render(widget["text"], True, text_color)
            text_rect = text_surface.get_rect(center=(x + w//2, y + h//2))
            surface.blit(text_surface, text_rect)
    
    def render(self, surface):
        """Render the scene"""
        # Clear background
        surface.fill(BACKGROUND_COLOR)
        
        # Title
        title_text = "Update Manager"
        title_surface = self.font.render(title_text, True, TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(160, 40))
        surface.blit(title_surface, title_rect)
        
        # Current version info
        if self.current_version:
            version_text = f"Current Version: {self.current_version}"
            version_surface = self.font.render(version_text, True, TEXT_COLOR)
            version_rect = version_surface.get_rect(center=(160, 70))
            surface.blit(version_surface, version_rect)
        
        # Status message
        if self.update_status:
            # Choose color based on status
            if "available" in self.update_status.lower():
                status_color = CAUTION_COLOR
            elif "latest" in self.update_status.lower():
                status_color = GOOD_COLOR
            elif "error" in self.update_status.lower() or "failed" in self.update_status.lower():
                status_color = WARNING_COLOR
            else:
                status_color = TEXT_COLOR
            
            status_surface = self.font.render(self.update_status, True, status_color)
            status_rect = status_surface.get_rect(center=(160, 95))
            surface.blit(status_surface, status_rect)
        
        # Render widgets
        for widget in self.widgets:
            self._render_widget(surface, widget)
        
        # Instructions
        instruction_text = "Tab to navigate, Enter/Space to activate, Esc to go back"
        instruction_surface = self.font.render(instruction_text, True, (150, 150, 150))
        instruction_rect = instruction_surface.get_rect(center=(160, 290))
        surface.blit(instruction_surface, instruction_rect)
