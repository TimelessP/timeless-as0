"""Fuel Management Scene (two-tank system)

Two vertical tanks (forward & aft) with:
 - Feed toggles per tank (engine feed enable)
 - Transfer sliders (rate 0..100%) transferring OUT to the other tank
 - Dump sliders (rate 0..100%) dumping fuel overboard
Actual fuel physics handled by CoreSimulator; scene only invokes setter methods.
If simulator lacks new methods (e.g., in tests), calls are safely ignored.
"""
from typing import Optional, List, Dict, Any

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover
    pygame = None  # type: ignore

BACKGROUND_COLOR = (20, 20, 30)
TEXT_COLOR = (230, 230, 240)
FOCUS_COLOR = (255, 200, 50)
HEADER_COLOR = (40, 80, 120)
HEADER_HEIGHT = 24
BAR_BG = (40, 40, 55)
FUEL_COLOR = (200, 120, 40)
SLIDER_TRACK = (70, 70, 90)
SLIDER_FILL = (120, 180, 255)
DUMP_FILL = (255, 100, 100)
BUTTON_COLOR = (60, 60, 80)
BUTTON_FOCUSED = (90, 90, 130)


class FuelScene:
    def __init__(self, simulator):
        self.simulator = simulator
        self.font = None
        self.is_text_antialiased = False
        self.widgets: List[Dict[str, Any]] = []
        self.focus_index = 0
        self.dragging_widget: Optional[int] = None
        # Keyboard adjustment granularities
        self.slider_step_small = 0.05
        self.slider_step_large = 0.15
        self._init_widgets()

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------
    def _init_widgets(self):
        self.widgets = []
        # Navigation buttons at bottom
        self.widgets.append({"id": "prev_scene", "type": "button", "position": [8, 290], "size": [60, 24], "text": "< [", "focused": True})
        self.widgets.append({"id": "next_scene", "type": "button", "position": [252, 290], "size": [60, 24], "text": "] >", "focused": False})
        
        # Feed toggles positioned above tanks with better spacing
        self.widgets.append({"id": "feed_forward", "type": "toggle", "position": [30, HEADER_HEIGHT + 6], "size": [80, 16], "text": "FWD FEED", "value": True, "focused": False})
        self.widgets.append({"id": "feed_aft", "type": "toggle", "position": [210, HEADER_HEIGHT + 6], "size": [80, 16], "text": "AFT FEED", "value": True, "focused": False})
        
        # Control sliders positioned in middle area between tanks and bottom buttons
        # Forward side: transfer and dump sliders side by side
        slider_y = 160  # Position between tanks and nav buttons
        slider_height = 60  # Shorter to fit better
        self.widgets.append({"id": "transfer_forward", "type": "slider", "position": [20, slider_y], "size": [35, slider_height], "value": 0.0, "vertical": True, "label": "XFER"})
        self.widgets.append({"id": "dump_forward", "type": "slider", "position": [65, slider_y], "size": [35, slider_height], "value": 0.0, "vertical": True, "label": "DUMP", "dump": True})
        
        # Aft side: dump and transfer sliders side by side (mirrored layout)
        self.widgets.append({"id": "dump_aft", "type": "slider", "position": [220, slider_y], "size": [35, slider_height], "value": 0.0, "vertical": True, "label": "DUMP", "dump": True})
        self.widgets.append({"id": "transfer_aft", "type": "slider", "position": [265, slider_y], "size": [35, slider_height], "value": 0.0, "vertical": True, "label": "XFER"})

    def set_font(self, font, is_text_antialiased=False):
        self.font = font
        self.is_text_antialiased = is_text_antialiased

    # ------------------------------------------------------------------
    # Helpers to call simulator safely
    # ------------------------------------------------------------------
    def _sim_call(self, method: str, *args):
        if hasattr(self.simulator, method):
            try:
                getattr(self.simulator, method)(*args)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Event Handling
    # ------------------------------------------------------------------
    def handle_event(self, event) -> Optional[str]:
        if not pygame:
            return None
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            current = self.widgets[self.focus_index] if 0 <= self.focus_index < len(self.widgets) else None

            # Scene navigation & exit
            if event.key == pygame.K_ESCAPE:
                return "scene_main_menu"
            elif event.key == pygame.K_LEFTBRACKET:  # '[' previous scene
                return self._get_prev_scene()
            elif event.key == pygame.K_RIGHTBRACKET:  # ']' next scene
                return self._get_next_scene()

            # Focus cycling
            if event.key == pygame.K_TAB:
                if mods & pygame.KMOD_SHIFT:
                    self._focus_prev()
                else:
                    self._focus_next()
                return None
            if event.key in (pygame.K_DOWN, pygame.K_PAGEDOWN):
                self._focus_next(); return None
            if event.key in (pygame.K_UP, pygame.K_PAGEUP):
                self._focus_prev(); return None

            # Activate
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._activate_focused()

            # Slider adjustments (arrows / plus / minus)
            if current and current["type"] == "slider":
                if event.key in (pygame.K_LEFT, pygame.K_MINUS):
                    self._adjust_slider(self.focus_index, -self.slider_step_small)
                elif event.key == pygame.K_RIGHT:
                    self._adjust_slider(self.focus_index, self.slider_step_small)
                elif event.key in (pygame.K_EQUALS,):  # '=' (often shift+'+' for US layout)
                    self._adjust_slider(self.focus_index, self.slider_step_small)
                elif event.key == pygame.K_PLUS:  # Some layouts have explicit plus
                    self._adjust_slider(self.focus_index, self.slider_step_large)
                elif event.key == pygame.K_KP_PLUS:
                    self._adjust_slider(self.focus_index, self.slider_step_large)
                elif event.key == pygame.K_KP_MINUS:
                    self._adjust_slider(self.focus_index, -self.slider_step_large)
                elif event.key == pygame.K_HOME:
                    self._set_slider(self.focus_index, 0.0)
                elif event.key == pygame.K_END:
                    self._set_slider(self.focus_index, 1.0)
                return None
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            idx = self._get_widget_at_pos(event.pos)
            if idx is not None:
                self._set_focus(idx)
                w = self.widgets[idx]
                if w["type"] == "button":
                    return self._activate_focused()
                if w["type"] == "toggle":
                    w["value"] = not w.get("value", False)
                    self._apply_toggle(w)
                if w["type"] == "slider":
                    self.dragging_widget = idx
                    self._set_slider_value_from_mouse(idx, event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_widget = None
        elif event.type == pygame.MOUSEMOTION and self.dragging_widget is not None:
            self._set_slider_value_from_mouse(self.dragging_widget, event.pos)
        return None

    def _get_widget_at_pos(self, pos) -> Optional[int]:
        if not pygame:
            return None
        x, y = pos
        for i, w in enumerate(self.widgets):
            wx, wy = w["position"]
            ww, wh = w["size"]
            if wx <= x <= wx + ww and wy <= y <= wy + wh:
                return i
        return None

    # ------------------------------------------------------------------
    # Widget operations
    # ------------------------------------------------------------------
    def _set_focus(self, idx: int):
        if idx < 0 or idx >= len(self.widgets):
            return
        for w in self.widgets:
            w["focused"] = False
        self.widgets[idx]["focused"] = True
        self.focus_index = idx

    def _focus_next(self):
        self._set_focus((self.focus_index + 1) % len(self.widgets))

    def _focus_prev(self):
        self._set_focus((self.focus_index - 1) % len(self.widgets))

    def _activate_focused(self) -> Optional[str]:
        w = self.widgets[self.focus_index]
        if w["id"] == "prev_scene":
            return self._get_prev_scene()
        if w["id"] == "next_scene":
            return self._get_next_scene()
        if w["type"] == "toggle":
            w["value"] = not w.get("value", False)
            self._apply_toggle(w)
        return None

    def _apply_toggle(self, widget):
        tank = "forward" if widget["id"] == "feed_forward" else "aft"
        self._sim_call("set_tank_feed", tank, widget["value"])

    def _adjust_slider(self, idx: int, delta: float):
        w = self.widgets[idx]
        w["value"] = max(0.0, min(1.0, w.get("value", 0.0) + delta))
        self._apply_slider(w)

    def _set_slider(self, idx: int, value: float):
        w = self.widgets[idx]
        w["value"] = max(0.0, min(1.0, value))
        self._apply_slider(w)

    def _set_slider_value_from_mouse(self, idx: int, pos):
        w = self.widgets[idx]
        x, y = pos
        wx, wy = w["position"]
        _, h = w["size"]
        rel = (wy + h - y) / h
        w["value"] = max(0.0, min(1.0, rel))
        self._apply_slider(w)

    def _apply_slider(self, widget):
        tank = "forward" if "forward" in widget["id"] else "aft"
        if widget.get("dump"):
            self._sim_call("set_dump_rate", tank, widget["value"])
        else:
            self._sim_call("set_transfer_rate", tank, widget["value"])

    # ------------------------------------------------------------------
    # Scene navigation helpers
    # ------------------------------------------------------------------
    def _get_prev_scene(self) -> str:
        return "scene_navigation"

    def _get_next_scene(self) -> str:
        return "scene_cargo"

    # ------------------------------------------------------------------
    # Update (sync UI with simulator state)
    # ------------------------------------------------------------------
    def update(self, dt: float):
        if not hasattr(self.simulator, "get_state"):
            return
        state = self.simulator.get_state()
        # Accept either new or legacy nested layout
        fuel = state.get("fuel") or state.get("engines", {}).get("fuel", {})
        tanks = fuel.get("tanks", {}) if isinstance(fuel, dict) else {}
        fwd = tanks.get("forward", {})
        aft = tanks.get("aft", {})
        # Sync toggles
        for wid in ("feed_forward", "feed_aft"):
            widget = next((w for w in self.widgets if w["id"] == wid), None)
            if widget:
                tank = fwd if "forward" in wid else aft
                feed_val = tank.get("feed", widget.get("value", True))
                widget["value"] = feed_val
        # Sync sliders (unless dragging)
        if self.dragging_widget is None:
            for wid in ("transfer_forward", "dump_forward", "transfer_aft", "dump_aft"):
                widget = next((w for w in self.widgets if w["id"] == wid), None)
                if widget:
                    tank = fwd if "forward" in wid else aft
                    if widget.get("dump"):
                        widget["value"] = tank.get("dumpRate", widget.get("value", 0.0))
                    else:
                        widget["value"] = tank.get("transferRate", widget.get("value", 0.0))

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def render(self, surface):
        if not pygame:
            return
        surface.fill(BACKGROUND_COLOR)
        # Header bar (match bridge style)
        pygame.draw.rect(surface, HEADER_COLOR, (0, 0, 320, HEADER_HEIGHT))
        pygame.draw.rect(surface, TEXT_COLOR, (0, 0, 320, HEADER_HEIGHT), 1)
        self._draw_text(surface, "FUEL", 160, 4, center=True)
        self._render_tanks(surface)
        for w in self.widgets:
            self._render_widget(surface, w)

    def _render_tanks(self, surface):
        state = self.simulator.get_state() if hasattr(self.simulator, "get_state") else {}
        fuel = state.get("fuel") or state.get("engines", {}).get("fuel", {})
        tanks = fuel.get("tanks", {}) if isinstance(fuel, dict) else {}
        fwd = tanks.get("forward", {})
        aft = tanks.get("aft", {})
        
        # Smaller tanks positioned to avoid widget conflicts
        tank_w = 50   # Narrower tanks
        tank_h = 100  # Shorter tanks 
        top_y = HEADER_HEIGHT + 30  # Below feed toggles
        
        # Position tanks with more space between them and controls
        fwd_rect = pygame.Rect(120, top_y, tank_w, tank_h)  # Centered in left half
        aft_rect = pygame.Rect(150, top_y, tank_w, tank_h)  # Centered in right half
        
        self._draw_tank(surface, fwd_rect, fwd, "FWD")
        self._draw_tank(surface, aft_rect, aft, "AFT")

    def _draw_tank(self, surface, rect, tank, label):
        pygame.draw.rect(surface, BAR_BG, rect, border_radius=4)
        level = tank.get("level", 0.0)
        capacity = tank.get("capacity", 1.0) or 1.0
        pct = max(0.0, min(1.0, level / capacity))
        fuel_height = int((rect.height - 4) * pct)
        fuel_rect = pygame.Rect(rect.x + 2, rect.y + rect.height - 2 - fuel_height, rect.width - 4, fuel_height)
        pygame.draw.rect(surface, FUEL_COLOR, fuel_rect, border_radius=4)
        pygame.draw.rect(surface, (110, 110, 130), rect, 1, border_radius=4)
        self._draw_text(surface, label, rect.centerx, rect.y - 12, center=True)
        # Show two decimals for better perception of change
        self._draw_text(surface, f"{level:.2f}/{capacity:.0f}g", rect.centerx, rect.y + rect.height + 4, center=True)

    def _render_widget(self, surface, widget):
        t = widget["type"]
        if t == "button":
            self._render_button(surface, widget)
        elif t == "toggle":
            self._render_toggle(surface, widget)
        elif t == "slider":
            self._render_slider(surface, widget)

    def _render_button(self, surface, widget):
        """Render button with bridge-style visuals for consistency."""
        x, y = widget["position"]; w, h = widget["size"]
        focused = widget.get("focused", False)
        # Match bridge scene palette
        bg_color = (80, 100, 120) if focused else (60, 80, 100)
        border_color = FOCUS_COLOR if focused else (120, 120, 120)
        text_color = FOCUS_COLOR if focused else TEXT_COLOR
        # Square corners (no rounding) to match bridge style
        pygame.draw.rect(surface, bg_color, (x, y, w, h))
        pygame.draw.rect(surface, border_color, (x, y, w, h), 1)
        if self.font:
            label = widget.get("text", "")
            img = self.font.render(label, self.is_text_antialiased, text_color)
            rect = img.get_rect()
            rect.x = x + (w - rect.width) // 2
            rect.y = y + (h - rect.height) // 2
            surface.blit(img, rect)

    def _render_toggle(self, surface, widget):
        x, y = widget["position"]; w, h = widget["size"]
        on = widget.get("value", False)
        base_color = (80, 140, 80) if on else (120, 70, 70)
        if widget.get("focused"):
            base_color = tuple(min(c + 40, 255) for c in base_color)
        pygame.draw.rect(surface, base_color, (x, y, w, h), border_radius=4)
        pygame.draw.rect(surface, (20, 20, 25), (x, y, w, h), 1, border_radius=4)
        txt = widget.get("text", "") + (" ON" if on else " OFF")
        self._draw_text(surface, txt, x + w / 2, y + 2, center=True)

    def _render_slider(self, surface, widget):
        x, y = widget["position"]; w, h = widget["size"]
        pygame.draw.rect(surface, SLIDER_TRACK, (x, y, w, h), border_radius=4)
        val = widget.get("value", 0.0)
        fill_h = int((h - 4) * val)
        fill_color = DUMP_FILL if widget.get("dump") else SLIDER_FILL
        pygame.draw.rect(surface, fill_color, (x + 2, y + h - 2 - fill_h, w - 4, fill_h), border_radius=4)
        pygame.draw.rect(surface, (30, 30, 40), (x, y, w, h), 1, border_radius=4)
        self._draw_text(surface, widget.get("label", ""), x + w / 2, y - 12, center=True)
        self._draw_text(surface, f"{val*100: .0f}%", x + w / 2, y + h + 2, center=True)
        if widget.get("focused"):
            pygame.draw.rect(surface, FOCUS_COLOR, (x - 2, y - 2, w + 4, h + 4), 1, border_radius=6)

    def _draw_text(self, surface, text, x, y, center=False):
        if not self.font or not pygame:
            return
        img = self.font.render(text, self.is_text_antialiased, TEXT_COLOR)
        rect = img.get_rect()
        if center:
            rect.centerx = int(x)
            rect.y = int(y)
        else:
            rect.x = int(x)
            rect.y = int(y)
        surface.blit(img, rect)
