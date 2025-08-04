# 🧱 Airship UI Rendering Spec (v1.0)
**Project:** Airship Zero UI System  
**Mode:** Brutalist, pixel-perfect, scalable retro UI  
**Resolution:** Logical `320x320`, scaled up  
**Font:** [Pixelify Sans](https://fonts.google.com/specimen/Pixelify+Sans)  
**Renderer:** Nearest-neighbor final scale pass  
**Scaling:** Arbitrary float scale (e.g., 2.75x, 3.13x) with center-align and letterboxing  

---

## 🎨 Canvas Model

### Logical Canvas
- Size: `320 x 320` pixels
- All UI elements are rendered *exclusively* in this space.
- Input coordinates (mouse, etc.) are mapped *to this space*, not screen pixels.

### Physical Output
- Rendered canvas is **scaled** using nearest-neighbor (not limited to integer scaling).
- Output may result in slightly “non-square” pixels.
- Surplus space is **letterboxed** (black bars, centered display).

---

## 🖋 Font and Text

### Font: Pixelify Sans
- Use Pixelify Sans at **native low resolution** (e.g., 8pt–12pt).
- Text is drawn *into the logical 320x320 buffer*.
- **Font anti-aliasing is allowed**, but final upscaling uses **nearest neighbor**.

```python
# Example text render to low-res canvas
font = load_font("PixelifySans-Regular.ttf", size=10)
text_surface = font.render("Battery A: ON", antialias=True, color=(255, 255, 255))
buffer.blit(text_surface, (x, y))
```

---

## 🧩 Widget Model

### Absolute Positioning
Each widget defines:
- `id`: unique name
- `type`: `label`, `button`, `slider`, `textbox`
- `position`: `[x, y]` in logical canvas pixels
- `size`: `[w, h]` in logical canvas pixels
- `focused`: `true/false`
- Optional metadata (`text`, `value`, etc.)

### JSON Example

```json
{
  "canvasSize": 320,
  "widgets": [
    {
      "id": "engine_status",
      "type": "label",
      "position": [8, 8],
      "size": [100, 16],
      "text": "Engine: OK",
      "focused": false
    },
    {
      "id": "toggle_battery",
      "type": "button",
      "position": [8, 32],
      "size": [140, 20],
      "text": "Battery A: ON",
      "focused": true
    },
    {
      "id": "fuel_slider",
      "type": "slider",
      "position": [8, 64],
      "size": [120, 20],
      "value": 0.65,
      "focused": false
    }
  ],
  "focusIndex": 1
}
```

---

## 🧠 Focus and Input

### Focus Model
- UI only allows *one focused widget* at a time.
- `focusIndex` is the active widget index.
- Keyboard input is routed to focused widget.
- `Enter`, `Arrow Keys`, `Tab`, `Esc` handled globally.

### Mouse Mapping
- Mouse click positions are scaled down to 320x320 before collision checks.
- Hit detection uses the logical buffer coordinates.

---

## 🖼️ Rendering Flow

```
1. Create offscreen buffer: 320x320
2. Draw all widgets (text, sliders, etc.) to this buffer
3. Scale buffer to window size using nearest-neighbor (float scale ok)
4. Center the scaled image on screen with black bars if needed
```

### Pseudocode

```python
LOGICAL_SIZE = 320

# Step 1: draw to buffer
buffer = pygame.Surface((LOGICAL_SIZE, LOGICAL_SIZE))
render_ui(buffer, widgets)

# Step 2: scale up
scale = min(window.width / LOGICAL_SIZE, window.height / LOGICAL_SIZE)
scaled = pygame.transform.scale(buffer, (LOGICAL_SIZE * scale, LOGICAL_SIZE * scale), special_flags=pygame.SCALE_NEAREST)

# Step 3: blit centered
x_offset = (window.width - scaled.get_width()) // 2
y_offset = (window.height - scaled.get_height()) // 2
window.blit(scaled, (x_offset, y_offset))
```

---

## 🎛️ Widget Behavior Summary

Tab and Shift-Tab to focus on next or previous.

Click/Enter to activate, Esc to deactivate (i.e. textbox editing is deactivated, but keeps focus).

| Type     | Interaction                              | Visual Behavior                     |
|----------|------------------------------------------|-------------------------------------|
| `label`  | No interaction                           | Draws static text                   |
| `button` | Click/Enter to toggle/activate           | Highlight when focused              |
| `slider` | Arrow keys or click/drag                 | Bar with filled portion, optional % |
| `textbox`| Input mode on click/Enter (not on focus) | Cursor blinks, accepts typed input  |

---

## 🧪 Dev Tips

- Use **grid-based alignment** (e.g., 8x8 cell grid).
- Scale text at native resolution — **scale after** drawing.
- Avoid blending effects (e.g., shadows), preserve retro style.
- No need for UI layering or modal stacks — *keep it flat*.
- Each scene renderer is a Callable which only renders this scene.

---

## 📍 Changelog

- v1.0 – Initial spec with 320x320 canvas, float-scale nearest-neighbor rendering, and absolute UI model

---

