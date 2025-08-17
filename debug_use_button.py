#!/usr/bin/env python3
"""
Debug the Use button enabling for book crates
"""
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from core_simulator import CoreSimulator
from scene_cargo import CargoScene
import uuid

def test_use_button_enabling():
    """Test Use button enabling when selecting book crates"""
    print("Testing Use Button Enabling...")
    
    # Create simulator and cargo scene
    sim = CoreSimulator()
    sim.start_new_game()
    cargo_scene = CargoScene(sim)
    
    # Add a book crate to cargo hold
    print("\n1. Adding book crate to cargo hold...")
    book_crate = {
        "id": str(uuid.uuid4()),
        "type": "books",
        "position": {"x": 40, "y": 80}
    }
    
    cargo_state = sim.get_cargo_state()
    cargo_state["cargoHold"].append(book_crate)
    sim._update_cargo_physics()
    print(f"   Book crate added: {book_crate['id']}")
    print(f"   Crate type: {book_crate['type']}")
    print(f"   Position: {book_crate['position']}")
    
    # Check if book type is usable
    crate_types = cargo_state.get("crateTypes", {})
    book_type_info = crate_types.get("books", {})
    print(f"   Book type usable: {book_type_info.get('usable', False)}")
    
    # Test initial state (no selection)
    print("\n2. Testing initial state (no selection)...")
    print(f"   Selected crate: {cargo_scene.selected_crate}")
    use_enabled = cargo_scene._is_widget_enabled("use_crate")
    print(f"   Use button enabled: {use_enabled}")
    
    # Test manual selection
    print("\n3. Testing manual selection...")
    cargo_scene.selected_crate = book_crate
    print(f"   Selected crate: {cargo_scene.selected_crate}")
    print(f"   Selected crate ID: {cargo_scene.selected_crate['id'] if cargo_scene.selected_crate else None}")
    print(f"   Selected crate type: {cargo_scene.selected_crate['type'] if cargo_scene.selected_crate else None}")
    
    # Test _is_crate_usable method
    is_usable = cargo_scene._is_crate_usable(cargo_scene.selected_crate)
    print(f"   Is crate usable: {is_usable}")
    
    # Test cargo hold check
    cargo_hold = cargo_state.get("cargoHold", [])
    crate_in_cargo_hold = any(c.get("id") == cargo_scene.selected_crate.get("id") for c in cargo_hold)
    print(f"   Crate in cargo hold: {crate_in_cargo_hold}")
    
    # Test winch attachment check
    winch = cargo_state.get("winch", {})
    attached_crate_id = winch.get("attachedCrate")
    is_attached = attached_crate_id == cargo_scene.selected_crate.get("id")
    print(f"   Is crate attached to winch: {is_attached}")
    
    # Test Use button enabled
    use_enabled = cargo_scene._is_widget_enabled("use_crate")
    print(f"   Use button enabled: {use_enabled}")
    
    # Test crate widget updates
    print("\n4. Testing crate widget updates...")
    cargo_scene._update_crate_widgets()
    print(f"   Number of crate widgets: {len(cargo_scene.crate_widgets)}")
    for i, cw in enumerate(cargo_scene.crate_widgets):
        print(f"   Crate widget {i}: ID={cw['crate_data']['id']}, type={cw['crate_data']['type']}")
    
    print("\n✅ Use button debugging complete!")

if __name__ == "__main__":
    test_use_button_enabling()
