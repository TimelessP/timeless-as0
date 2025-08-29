#!/usr/bin/env python3
"""
Quick test to verify observatory scene navigation chain
"""

import sys
import os
import pygame

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_simulator import get_simulator
from scene_library import LibraryScene
from scene_observatory import ObservatoryScene
from scene_bridge import BridgeScene

def test_scene_navigation():
    """Test that scene navigation links work correctly"""
    
    print("🧪 Testing Observatory Scene Navigation Chain...")
    
    # Initialize simulator
    simulator = get_simulator()
    
    # Create scenes
    library = LibraryScene(simulator)
    observatory = ObservatoryScene(simulator)
    bridge = BridgeScene(simulator)
    
    print("✅ Scenes created successfully")
    
    # Test navigation chain
    print("\n🔗 Testing navigation chain:")
    
    # Library -> Observatory
    library_next = library._get_next_scene()
    print(f"Library next scene: {library_next}")
    assert library_next == "scene_observatory", f"Expected 'scene_observatory', got '{library_next}'"
    
    # Observatory -> Bridge
    observatory_next = observatory._get_next_scene()
    print(f"Observatory next scene: {observatory_next}")
    assert observatory_next == "scene_bridge", f"Expected 'scene_bridge', got '{observatory_next}'"
    
    # Observatory <- Library
    observatory_prev = observatory._get_prev_scene()
    print(f"Observatory prev scene: {observatory_prev}")
    assert observatory_prev == "scene_library", f"Expected 'scene_library', got '{observatory_prev}'"
    
    # Bridge <- Observatory
    bridge_prev = bridge._get_prev_scene()
    print(f"Bridge prev scene: {bridge_prev}")
    assert bridge_prev == "scene_observatory", f"Expected 'scene_observatory', got '{bridge_prev}'"
    
    print("\n✅ All navigation tests passed!")
    print("🎯 Observatory scene successfully integrated into circular scene chain:")
    print("   Library ↔ Observatory ↔ Bridge")

if __name__ == "__main__":
    test_scene_navigation()
