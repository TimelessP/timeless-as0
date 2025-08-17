#!/usr/bin/env python3
"""
Test the Use button functionality for books in cargo scene
"""
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from core_simulator import CoreSimulator
from scene_cargo import CargoScene
import uuid

def test_use_button_restrictions():
    """Test that Use button only works for books in cargo hold, not loading bay"""
    print("Testing Use Button Restrictions...")
    
    # Create simulator and cargo scene
    sim = CoreSimulator()
    sim.start_new_game()
    cargo_scene = CargoScene(sim)
    
    # Test 1: Book in cargo hold should be usable
    print("\n1. Testing book in cargo hold (should be usable)...")
    book_in_cargo = {
        "id": str(uuid.uuid4()),
        "type": "books",
        "position": {"x": 40, "y": 80}
    }
    
    cargo_state = sim.get_cargo_state()
    cargo_state["cargoHold"].append(book_in_cargo)
    sim._update_cargo_physics()
    
    # Select the book and test if Use is enabled
    cargo_scene.selected_crate = book_in_cargo
    use_enabled = cargo_scene._is_widget_enabled("use_crate")
    print(f"   Book in cargo hold - Use enabled: {use_enabled}")
    assert use_enabled, "Should be able to use book in cargo hold"
    
    # Test 2: Book in loading bay should NOT be usable
    print("\n2. Testing book in loading bay (should NOT be usable)...")
    book_in_loading = {
        "id": str(uuid.uuid4()),
        "type": "books", 
        "position": {"x": 200, "y": 80}
    }
    
    cargo_state["loadingBay"].append(book_in_loading)
    
    # Select the book in loading bay and test if Use is disabled
    cargo_scene.selected_crate = book_in_loading
    use_enabled = cargo_scene._is_widget_enabled("use_crate")
    print(f"   Book in loading bay - Use enabled: {use_enabled}")
    assert not use_enabled, "Should NOT be able to use book in loading bay"
    
    # Test 3: Non-usable crate in cargo hold should NOT be usable
    print("\n3. Testing non-usable crate in cargo hold (should NOT be usable)...")
    spare_parts_in_cargo = {
        "id": str(uuid.uuid4()),
        "type": "spare_parts",  # Not usable
        "position": {"x": 60, "y": 100}
    }
    
    cargo_state["cargoHold"].append(spare_parts_in_cargo)
    
    # Select non-usable crate and test if Use is disabled
    cargo_scene.selected_crate = spare_parts_in_cargo
    use_enabled = cargo_scene._is_widget_enabled("use_crate")
    print(f"   Spare parts in cargo hold - Use enabled: {use_enabled}")
    assert not use_enabled, "Should NOT be able to use non-usable crate"
    
    # Test 4: Attached book should NOT be usable
    print("\n4. Testing attached book (should NOT be usable)...")
    # Attach the book to winch
    cargo_state["winch"]["attachedCrate"] = book_in_cargo["id"]
    
    cargo_scene.selected_crate = book_in_cargo
    use_enabled = cargo_scene._is_widget_enabled("use_crate")
    print(f"   Attached book - Use enabled: {use_enabled}")
    assert not use_enabled, "Should NOT be able to use attached book"
    
    # Test 5: Actually using a book should work
    print("\n5. Testing actual book usage...")
    # Detach the book first
    cargo_state["winch"]["attachedCrate"] = None
    
    # Count books in library before
    books_before = len(sim.get_library_books())
    print(f"   Books in library before: {books_before}")
    
    # Use the book
    cargo_scene.selected_crate = book_in_cargo
    success = sim.use_crate(book_in_cargo["id"])
    print(f"   Use crate success: {success}")
    assert success, "Should be able to use book successfully"
    
    # Check books in library after
    books_after = len(sim.get_library_books())
    print(f"   Books in library after: {books_after}")
    assert books_after == books_before + 1, "Should have one more book in library"
    
    # Check that book was removed from cargo
    cargo_state = sim.get_cargo_state()
    cargo_hold = cargo_state.get("cargoHold", [])
    book_still_in_cargo = any(c.get("id") == book_in_cargo["id"] for c in cargo_hold)
    print(f"   Book still in cargo: {book_still_in_cargo}")
    assert not book_still_in_cargo, "Book should be removed from cargo after use"
    
    print("\n✅ All Use button restriction tests passed!")

if __name__ == "__main__":
    test_use_button_restrictions()
