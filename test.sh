#!/bin/bash
# Test script for Airship Zero UI Foundation
# Comprehensive testing with coverage reporting

set -e  # Exit on any error

echo "🧪 Running Airship Zero UI Foundation Test Suite"
echo "   TDD validation with comprehensive coverage"
echo ""

# Check if we have UV available
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install UV first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Run tests with coverage
echo "📊 Running unit tests with coverage analysis..."
echo ""

uv run pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

echo ""
echo "📈 Coverage report generated in htmlcov/index.html"
echo "🔍 Open htmlcov/index.html in a browser to see detailed coverage"
echo ""

# Optional: Run specific test categories
if [ "$1" = "ui" ]; then
    echo "🎨 Running UI-specific tests only..."
    uv run pytest tests/ -v -m ui
elif [ "$1" = "layout" ]; then
    echo "📐 Running layout tests only..."
    uv run pytest tests/test_ui_foundation.py::TestFlowContainer -v
elif [ "$1" = "blinken" ]; then
    echo "💡 Running BlinkenLight tests only..."
    uv run pytest tests/test_ui_foundation.py::TestBlinkenLight -v
fi

echo "✅ Test suite completed successfully!"
