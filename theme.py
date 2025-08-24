# Crate type color palette for cargo scene (wood/paint/ink inspired, not bright)
# Map: crate_type_id -> {"outline": hex, "fill": hex}
# Example usage: CRATE_TYPE_COLORS["fuel_drum"]["fill"]
CRATE_TYPE_COLORS = {
	"fuel_drum":     {"outline": "#B97A56", "fill": "#8B5C2A"},   # Oiled wood barrel
	"books":         {"outline": "#6B4F2B", "fill": "#C2B280"},   # Old book crate
	"medical_supplies": {"outline": "#A89C94", "fill": "#E5D8C0"}, # Canvas/linen
	"food_rations":  {"outline": "#7A6A4F", "fill": "#B7A16A"},   # Burlap sack
	"spare_parts":   {"outline": "#5C5C5C", "fill": "#A0A0A0"},   # Metal crate
	"luxury_goods":  {"outline": "#C2B280", "fill": "#E6D8AD"},   # Fancy wood
}
# Navigation map color filter parameters
# NAV_MAP_FILTER_PARAMS controls the color transformation applied to the navigation map image on load.
# To disable filtering (no color change), set to (1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0):
#   (r_mult, g_mult, b_mult, r_add, g_add, b_add, sepia_strength)
# Example for 50% sepia effect:
#   r_mult=1.0, g_mult=0.85, b_mult=0.6, r_add=20, g_add=10, b_add=-30, sepia_strength=0.5
# - r_mult/g_mult/b_mult: Per-channel multipliers (reduce saturation)
# - r_add/g_add/b_add: Per-channel additive offsets (warm up/cool down)
# - sepia_strength: 0.0 = no sepia, 1.0 = full sepia, 0.5 = moderate sepia
NAV_MAP_FILTER_PARAMS = (1.0, 0.85, 0.6, 20, 10, -30, 0.5)
# Navigation scene extras
NAV_BACKGROUND_COLOR = (10, 20, 30)
NAV_TEXT_COLOR = (255, 255, 255)
NAV_POSITION_COLOR = (255, 100, 100)
NAV_AIRSHIP_COLOR = (120, 30, 30)
NAV_AIRSHIP_RANGE_COLOR = (120, 30, 30)
NAV_ROUTE_COLOR = (100, 255, 100)
NAV_WAYPOINT_TEXT_COLOR = (90, 60, 40)
NAV_OCEAN_COLOR = (0, 50, 100)
NAV_LAND_COLOR = (50, 80, 50)
NAV_NIGHT_MASK_COLOR = (0, 0, 0)
NAV_DAYLIGHT_MASK_COLOR = (255, 255, 255)
NAV_WIDGET_BG = (60, 60, 80)
NAV_WIDGET_BG_FOCUSED = (80, 80, 120)
NAV_WIDGET_BORDER_DISABLED = (128, 128, 128)
# Fuel scene header color
FUEL_HEADER_COLOR = (100, 80, 40)  # Distinctive brass/bronze for fuel scene
# Cargo scene extras
BUTTON_BG_FOCUSED = (80, 100, 120)
BUTTON_BG = (60, 80, 100)
BUTTON_BORDER_DISABLED = (60, 60, 60)
BUTTON_TEXT_DISABLED = (100, 100, 100)
DEFAULT_GRAY = (128, 128, 128)
# Bridge scene exotic/extra colors
INSTRUMENT_BG_COLOR = (30, 50, 70)  # Custom blue-grey for instrument background
INSTRUMENT_BORDER_COLOR = (255, 255, 255)
SKY_COLOR = (70, 120, 190)  # Sky blue
GROUND_COLOR = (110, 80, 50)  # Earth brown
HORIZON_LINE_COLOR = (255, 255, 255)
PITCH_TICK_COLOR = (230, 230, 230)
PITCH_LABEL_COLOR = (240, 240, 240)
PITCH_TEXT_COLOR = (255, 255, 255)
WIDGET_BG_COLOR = (40, 40, 60)  # Slightly blue-grey for background
WIDGET_BORDER_DISABLED_COLOR = (120, 120, 120)
BUTTON_BG_FOCUSED = (80, 100, 120)
BUTTON_BG = (60, 80, 100)
TEXTBOX_BG_ACTIVE = (40, 60, 40)
TEXTBOX_BG_FOCUSED = (50, 50, 80)
TEXTBOX_BG_DISABLED = (30, 30, 50)
TEXTBOX_BORDER_DISABLED = (100, 100, 100)
TEXTBOX_TEXT_DISABLED = (180, 180, 180)
# Logical resolution for all scenes
LOGICAL_SIZE = 320
# Main menu and general UI extras
SUBTITLE_COLOR = (180, 180, 180)  # Silver-grey for subtitle
DISABLED_TEXT_COLOR = (100, 100, 100)  # For disabled button text and borders
"""
Theme and color palette for Airship Zero
Wood, brass, and ink inspired colors for a unified steampunk look
"""

# General UI colors
BACKGROUND_COLOR = (32, 24, 16)  # Deep brown, wood panel
TEXT_COLOR = (240, 220, 180)     # Warm parchment/ivory
FOCUS_COLOR = (255, 210, 80)     # Brass/gold highlight
BUTTON_COLOR = (90, 60, 30)      # Wood button
BUTTON_FOCUSED_COLOR = (140, 100, 40)  # Brass button
BUTTON_DISABLED_COLOR = (60, 40, 30)   # Dimmed wood
BUTTON_BORDER_DISABLED_COLOR = (50, 30, 20)
BUTTON_BORDER_COLOR = (240, 220, 180)     # Warm parchment/ivory
BUTTON_BORDER_FOCUSED_COLOR = (255, 210, 80)  # Brass/gold highlight
BUTTON_TEXT_COLOR = (240, 220, 180)    # Ivory
BUTTON_TEXT_FOCUSED_COLOR = (240, 220, 180)  # Ivory
BUTTON_TEXT_DISABLED_COLOR = (150, 130, 100)  # Dimmed parchment

# Alerts and status
WARNING_COLOR = (220, 100, 60)   # Red-orange warning
CAUTION_COLOR = (255, 200, 100)  # Yellow caution
GOOD_COLOR = (120, 200, 100)     # Verdigris green

# Scene headers (for subtle scene distinction)
BRIDGE_HEADER_COLOR = (60, 40, 20)      # Walnut brown
ENGINE_HEADER_COLOR = (100, 60, 30)     # Mahogany
CARGO_HEADER_COLOR = (120, 100, 60)     # Lighter wood
CREW_HEADER_COLOR = (60, 80, 60)        # Olive green
COMMS_HEADER_COLOR = (60, 60, 100)      # Muted blue
MISSION_HEADER_COLOR = (80, 60, 40)     # Brass/bronze
NAV_HEADER_COLOR = (36, 48, 80)        # Unique blue, similar tonal range, for nav scene
LIBRARY_HEADER_COLOR = (60, 40, 60)     # Olive green

# Book/reading scene (keep as is for ink & paper)
BOOK_TEXT_COLOR = (60, 50, 40)
PAPER_COLOR = (240, 230, 220)  # Slightly dimmed for dark mode
PAGE_BORDER_COLOR = (139, 69, 19)
BOOKMARK_COLOR = (70, 130, 200)
BOOKMARK_PLACEHOLDER_COLOR = (40, 60, 100)


# Library scene book list colors
BOOK_LIST_COLOR = BUTTON_COLOR              # Use standard button color for book list background
SELECTED_BOOK_COLOR = BUTTON_FOCUSED_COLOR        # Deep gold for selected book (matches BUTTON_FOCUSED_COLOR)
BOOK_LIST_FOCUSED_COLOR = (180, 140, 40)    # Saturated brass for focused selection

# Editable user book colors (for books in Documents/AirshipZero/books/)
BOOK_LIST_EDIT_TEXT_COLOR = (180, 200, 140)  # Muted verdigris/olive for editable user book text
BOOK_LIST_EDIT_TEXT_COLOR_SELECTED = (255, 230, 180)  # Warm parchment for selected editable book
BOOK_LIST_EDIT_BG_COLOR_SELECTED = (80, 70, 40)  # Deep brass/bronze background for selected editable book

# Navigation map (keep as is for ink look)
MAP_BACKGROUND_COLOR = (10, 20, 30)
MAP_POSITION_COLOR = (255, 100, 100)
MAP_AIRSHIP_COLOR = (120, 30, 30)
MAP_ROUTE_COLOR = (100, 255, 100)
MAP_WAYPOINT_TEXT_COLOR = (90, 60, 40)

# Miscellaneous
GRID_COLOR = (40, 40, 50)
WINCH_COLOR = (150, 150, 150)
CABLE_COLOR = (120, 120, 120)
CARGO_HOLD_COLOR = (30, 50, 40)
LOADING_BAY_COLOR = (50, 40, 30)
AREA_BORDER_COLOR = (80, 80, 80)
SELECTED_CRATE_COLOR = (255, 255, 100)
VALID_PLACEMENT_COLOR = (100, 255, 100)
INVALID_PLACEMENT_COLOR = (255, 100, 100)

# Sliders, bars, etc.
FUEL_COLOR = (200, 120, 40)
SLIDER_FILL = (120, 180, 255)
DUMP_FILL = (255, 100, 100)

# Fuel toggle (feed) button colors
FUEL_TOGGLE_ON_COLOR = (80, 140, 80)   # Green for feed ON
FUEL_TOGGLE_OFF_COLOR = (120, 70, 70)  # Red for feed OFF
