#!/bin/bash

# Simple test runner for Airship Zero
# Runs the application and checks for basic functionality

echo "🚁 Testing Airship Zero UI System..."
echo "Resolution: 320x320 logical, brutally simple architecture"
echo "Font: Pixelify Sans (retro pixel-perfect goodness)"
echo ""

# Check if pygame is available
python3 -c "import pygame; print('✅ Pygame available')" 2>/dev/null || {
    echo "❌ Pygame not available - installing..."
    pip install pygame
}

# Check if Pixelify Sans font exists
if [ -f "assets/fonts/Pixelify_Sans/static/PixelifySans-Regular.ttf" ]; then
    echo "✅ Pixelify Sans font found"
else
    echo "❌ Pixelify Sans font missing"
fi

# Check if all scene files exist
scenes=("scene_main_menu.py" "scene_bridge.py" "scene_engine_room.py")
for scene in "${scenes[@]}"; do
    if [ -f "$scene" ]; then
        echo "✅ $scene found"
    else
        echo "❌ $scene missing"
        exit 1
    fi
done

echo ""
echo "🎮 Starting Airship Zero..."
echo "Expected behavior:"
echo "  - Main menu with New Game, Resume Game (disabled), Settings, Quit"
echo "  - New Game -> Bridge scene with flight instruments"
echo "  - Engine Room button -> Engine room with controls and gauges"
echo "  - ESC in scenes -> return to main menu"
echo "  - 320x320 logical resolution scaled to window"
echo ""
echo "Controls:"
echo "  - Tab/Shift+Tab or Arrow keys to navigate"
echo "  - Enter/Space to activate"
echo "  - ESC to go back/quit"
echo "  - Mouse clicks also work"
echo ""

# Run the application
python3 main.py
