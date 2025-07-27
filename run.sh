#!/bin/bash
# Run script for Airship Zero UI Foundation
# Quick launcher for development and testing

set -e  # Exit on any error

echo "🚀 Starting Airship Zero UI Foundation..."
echo "   Using UV environment management"
echo ""

# Check if we have UV available
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install UV first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Run the UI foundation
echo "🎮 Launching UI with proper layout containers..."
uv run python ui_foundation.py

echo ""
echo "✅ Airship Zero session ended gracefully"
