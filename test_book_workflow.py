#!/usr/bin/env python3
"""
Test the complete book workflow: cargo -> library -> book reading
"""
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from core_simulator import CoreSimulator
import uuid

def test_book_workflow():
    """Test the complete book workflow"""
    print("Testing Complete Book Workflow...")
    
    # Create a new simulator
    sim = CoreSimulator()
    sim.start_new_game()
    
    # Simulate adding a book crate to cargo hold
    print("1. Adding book crate to cargo hold...")
    cargo_state = sim.get_cargo_state()
    book_crate = {
        "id": str(uuid.uuid4()),
        "type": "books",
        "position": {"x": 40, "y": 80}
    }
    cargo_state["cargoHold"].append(book_crate)
    sim._update_cargo_physics()
    
    print(f"   Book crate added: {book_crate['id']}")
    
    # Test using the book crate
    print("2. Using book crate to add to library...")
    success = sim.use_crate(book_crate["id"])
    print(f"   Use crate success: {success}")
    assert success, "Should be able to use book crate"
    
    # Check that book was added to library
    books = sim.get_library_books()
    print(f"   Books in library: {books}")
    assert len(books) == 1, "Should have one book in library"
    
    # Check that crate was removed from cargo
    cargo_state = sim.get_cargo_state()
    cargo_hold = cargo_state.get("cargoHold", [])
    crate_ids = [crate.get("id") for crate in cargo_hold]
    print(f"   Remaining crates in cargo: {len(cargo_hold)}")
    assert book_crate["id"] not in crate_ids, "Book crate should be removed"
    
    # Test moving book back to cargo
    print("3. Moving book back to cargo...")
    book_filename = books[0]
    success = sim.remove_book_from_library(book_filename)
    print(f"   Remove from library success: {success}")
    assert success, "Should be able to remove book from library"
    
    # Check library is empty
    books_after = sim.get_library_books()
    print(f"   Books in library after removal: {books_after}")
    assert len(books_after) == 0, "Library should be empty"
    
    # Check book crate was added back to cargo
    cargo_state = sim.get_cargo_state()
    cargo_hold = cargo_state.get("cargoHold", [])
    book_crates = [crate for crate in cargo_hold if crate.get("type") == "books"]
    print(f"   Book crates in cargo: {len(book_crates)}")
    assert len(book_crates) == 1, "Should have one book crate in cargo"
    
    print("✅ Complete book workflow test passed!")

def test_book_scene_creation():
    """Test that book scenes can be created"""
    print("Testing BookScene creation...")
    
    # Test with an existing book file
    from scene_book import BookScene
    
    sim = CoreSimulator()
    book_scene = BookScene(sim, "wind-in-the-wires.md")
    
    print(f"   Book title: {book_scene.book_title}")
    print(f"   Book filename: {book_scene.book_filename}")
    
    # Test that the book file exists
    book_path = os.path.join("assets", "books", "wind-in-the-wires.md")
    assert os.path.exists(book_path), f"Book file should exist: {book_path}"
    
    print("✅ BookScene creation test passed!")

if __name__ == "__main__":
    test_book_workflow()
    test_book_scene_creation()
