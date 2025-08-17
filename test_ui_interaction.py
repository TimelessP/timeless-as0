#!/usr/bin/env python3
"""
Test the actual UI interaction for selecting book crates
"""
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from core_simulator import CoreSimulator
from scene_cargo import CargoScene
import uuid
import pygame

def test_ui_interaction():
    """Test the UI interaction for selecting book crates"""
    print("Testing UI Interaction for Book Selection...")
    
    # Initialize pygame (needed for some operations)
    pygame.init()
    
    # Create simulator and cargo scene
    sim = CoreSimulator()
    sim.start_new_game()
    cargo_scene = CargoScene(sim)
    
    # Add a book crate to cargo hold
    print("\n1. Setting up book crate in cargo hold...")
    book_crate = {
        "id": str(uuid.uuid4()),
        "type": "books",
        "position": {"x": 40, "y": 80}
    }
    
    cargo_state = sim.get_cargo_state()
    cargo_state["cargoHold"].append(book_crate)
    sim._update_cargo_physics()
    print(f"   Book crate added: {book_crate['id']}")
    
    # Update crate widgets (this should happen automatically)
    cargo_scene._update_crate_widgets()
    print(f"   Crate widgets updated: {len(cargo_scene.crate_widgets)} widgets")
    
    # Test 1: Click selection
    print("\n2. Testing click selection...")
    # Find the crate position
    crate_pos = (book_crate["position"]["x"] + 8, book_crate["position"]["y"] + 8)  # Click center of crate
    print(f"   Clicking at position: {crate_pos}")
    
    # Simulate getting crate at position
    clicked_crate = cargo_scene._get_crate_at_pos(crate_pos)
    print(f"   Found crate at position: {clicked_crate is not None}")
    if clicked_crate:
        print(f"   Clicked crate ID: {clicked_crate['id']}")
        print(f"   Matches book crate: {clicked_crate['id'] == book_crate['id']}")
    
    # Simulate the click selection logic
    if clicked_crate is not None:
        if cargo_scene.selected_crate and cargo_scene.selected_crate["id"] == clicked_crate["id"]:
            cargo_scene.selected_crate = None  # Deselect if same crate
        else:
            cargo_scene.selected_crate = clicked_crate  # Select new crate
    
    print(f"   Selected crate after click: {cargo_scene.selected_crate is not None}")
    if cargo_scene.selected_crate:
        print(f"   Selected crate ID: {cargo_scene.selected_crate['id']}")
    
    # Test Use button state after click selection
    use_enabled_after_click = cargo_scene._is_widget_enabled("use_crate")
    print(f"   Use button enabled after click: {use_enabled_after_click}")
    
    # Test 2: Tab navigation selection
    print("\n3. Testing Tab navigation selection...")
    
    # Reset selection
    cargo_scene.selected_crate = None
    
    # Focus on the crate using Tab navigation
    cargo_scene.focused_widget = len(cargo_scene.widgets)  # Focus on first crate
    cargo_scene._set_focus(cargo_scene.focused_widget)
    
    print(f"   Focused widget index: {cargo_scene.focused_widget}")
    print(f"   Total widgets: {len(cargo_scene.widgets)}")
    print(f"   Total crate widgets: {len(cargo_scene.crate_widgets)}")
    
    # Simulate Enter/Space activation
    result = cargo_scene._activate_focused()
    print(f"   Activation result: {result}")
    print(f"   Selected crate after Tab+Enter: {cargo_scene.selected_crate is not None}")
    if cargo_scene.selected_crate:
        print(f"   Selected crate ID: {cargo_scene.selected_crate['id']}")
    
    # Test Use button state after Tab selection
    use_enabled_after_tab = cargo_scene._is_widget_enabled("use_crate")
    print(f"   Use button enabled after Tab+Enter: {use_enabled_after_tab}")
    
    # Test 3: Widget rendering state
    print("\n4. Testing widget rendering state...")
    for widget in cargo_scene.widgets:
        if widget["id"] == "use_crate":
            enabled = cargo_scene._is_widget_enabled(widget["id"])
            print(f"   Use widget enabled: {enabled}")
            print(f"   Use widget focused: {widget.get('focused', False)}")
            break
    
    print("\n✅ UI interaction testing complete!")

if __name__ == "__main__":
    test_ui_interaction()
