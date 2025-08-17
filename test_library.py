#!/usr/bin/env python3
"""
Test script for the library system
"""
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from core_simulator import CoreSimulator

def test_library_system():
    """Test the library functionality"""
    print("Testing Library System...")
    
    # Create a new simulator
    sim = CoreSimulator()
    sim.start_new_game()
    
    # Test initial library state
    books = sim.get_library_books()
    print(f"Initial library books: {books}")
    assert len(books) == 0, "Library should start empty"
    
    # Test adding books
    print("Testing add_random_book_to_library...")
    success = sim.add_random_book_to_library()
    print(f"Added book successfully: {success}")
    assert success, "Should be able to add a book"
    
    books = sim.get_library_books()
    print(f"Books after adding one: {books}")
    assert len(books) == 1, "Should have one book"
    
    # Add a few more books
    for i in range(3):
        success = sim.add_random_book_to_library()
        print(f"Added book {i+2}: {success}")
    
    books = sim.get_library_books()
    print(f"Books after adding more: {books}")
    print(f"Total books: {len(books)}")
    
    # Test removing a book
    if books:
        book_to_remove = books[0]
        print(f"Testing removal of: {book_to_remove}")
        success = sim.remove_book_from_library(book_to_remove)
        print(f"Removed book successfully: {success}")
        
        books_after = sim.get_library_books()
        print(f"Books after removal: {books_after}")
        assert book_to_remove not in books_after, "Book should be removed"
        
        # Check if book crate was added to cargo
        cargo_state = sim.get_cargo_state()
        cargo_hold = cargo_state.get("cargoHold", [])
        print(f"Cargo hold has {len(cargo_hold)} items")
        
        # Look for book crates
        book_crates = [crate for crate in cargo_hold if crate.get("type") == "books"]
        print(f"Book crates in cargo: {len(book_crates)}")
    
    print("✅ Library system tests passed!")

if __name__ == "__main__":
    test_library_system()
