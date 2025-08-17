#!/usr/bin/env python3
"""
Complete test of the book workflow:
1. Use book crate in cargo
2. Navigate to library 
3. Verify book appears in library
4. Read book
5. Move book back to cargo
"""

import pygame
import sys
from core_simulator import get_simulator
from scene_library import LibraryScene
from scene_cargo import CargoScene

def test_complete_workflow():
    print("🧪 Testing Complete Book Workflow")
    print("=" * 50)
    
    # Initialize pygame (needed for scene creation)
    pygame.init()
    
    # Initialize simulator
    simulator = get_simulator()
    simulator.load_game()
    
    print("📋 Initial State:")
    initial_books = simulator.get_library_books()
    initial_book_count = len(initial_books)  # Capture count to avoid reference issues
    cargo_state = simulator.get_cargo_state()
    initial_book_crates = [c for c in cargo_state['cargoHold'] if c.get('type') == 'books']
    print(f"   Books in library: {initial_book_count} {initial_books}")
    print(f"   Book crates in cargo: {len(initial_book_crates)}")
    
    if not initial_book_crates:
        print("❌ No book crates available for testing")
        return False
    
    print(f"\n📦 Step 1: Using book crate in cargo scene")
    crate_id = initial_book_crates[0]['id']
    print(f"   Using crate: {crate_id}")
    success = simulator.use_crate(crate_id)
    print(f"   Use success: {success}")
    
    if not success:
        print("❌ Failed to use book crate")
        return False
    
    # Check post-use state
    post_use_books = simulator.get_library_books()
    cargo_state_after = simulator.get_cargo_state()
    remaining_book_crates = [c for c in cargo_state_after['cargoHold'] if c.get('type') == 'books']
    
    print(f"   Books in library after use: {len(post_use_books)} {post_use_books}")
    print(f"   Book crates remaining: {len(remaining_book_crates)}")
    
    # Debug the comparison
    print(f"   Debug: {len(post_use_books)} <= {initial_book_count} = {len(post_use_books) <= initial_book_count}")
    
    if len(post_use_books) <= initial_book_count:
        print("❌ No new book was added to library")
        return False
    
    new_books = set(post_use_books) - set(initial_books)
    if not new_books:
        print("❌ No new books found in set difference")
        return False
    new_book = list(new_books)[0]
    print(f"   ✅ New book added: {new_book}")
    
    print(f"\n📚 Step 2: Testing library scene auto-refresh")
    library_scene = LibraryScene(simulator)
    print(f"   Library scene initial books: {len(library_scene.books)}")
    
    # The library scene should already have the correct books since it was created after the book was added
    # But let's test the auto-refresh by simulating an update cycle
    library_scene.update(0.1)
    print(f"   Library scene books after update: {len(library_scene.books)}")
    print(f"   Books in scene: {library_scene.books}")
    
    if new_book not in library_scene.books:
        print(f"❌ New book {new_book} not found in library scene")
        return False
    
    print(f"   ✅ New book {new_book} visible in library scene")
    
    print(f"\n📖 Step 3: Testing book reading")
    # Find the new book in the library scene
    try:
        book_index = library_scene.books.index(new_book)
        library_scene.selected_book_index = book_index
        
        # Test reading the book (this should return a scene transition)
        read_result = library_scene._read_selected_book()
        expected_scene = f"scene_book:{new_book}"
        
        print(f"   Reading book at index {book_index}: {new_book}")
        print(f"   Read result: {read_result}")
        print(f"   Expected: {expected_scene}")
        
        if read_result == expected_scene:
            print(f"   ✅ Book reading works correctly")
        else:
            print(f"   ❌ Book reading failed - unexpected result")
            return False
            
    except ValueError:
        print(f"❌ Could not find new book {new_book} in library scene books")
        return False
    
    print(f"\n📦 Step 4: Testing move book back to cargo")
    initial_cargo_crates = len(cargo_state_after['cargoHold'])
    
    # Move the book back to cargo
    library_scene._move_book_to_cargo()
    
    # Check results
    final_books = simulator.get_library_books()
    final_cargo_state = simulator.get_cargo_state()
    final_cargo_crates = len(final_cargo_state['cargoHold'])
    
    print(f"   Books in library after move: {len(final_books)} {final_books}")
    print(f"   Cargo crates after move: {final_cargo_crates} (was {initial_cargo_crates})")
    
    if len(final_books) >= len(post_use_books):
        print("❌ Book was not removed from library")
        return False
        
    if final_cargo_crates <= initial_cargo_crates:
        print("❌ No new crate was added to cargo")
        return False
    
    print(f"   ✅ Book successfully moved back to cargo")
    
    print(f"\n🎉 Complete Book Workflow Test: PASSED")
    print("=" * 50)
    return True

if __name__ == "__main__":
    try:
        success = test_complete_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        sys.exit(1)
