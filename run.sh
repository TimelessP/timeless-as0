#!/bin/bash
# Run script for Airship Zero
# Steam & Copper Dreams in 320x320 pixels

set -e  # Exit on any error

echo "🚀 Starting Airship Zero..."
echo "   Steam & Copper Dreams Edition"
echo "   Retro airship simulation in glorious 320x320"
echo ""

# Check if we have UV available
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install UV first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Run the main application
echo "🎮 Launching Airship Zero main application..."
uv run python main.py

echo ""
echo "✅ Airship Zero session ended gracefully"
