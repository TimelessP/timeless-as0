import os
import tempfile
import sys
import shutil
import pytest
import importlib
from core_simulator import get_simulator

def setup_module(module):
    # Ensure a clean singleton for each test run
    if hasattr(get_simulator, '_simulator'):
        get_simulator._simulator = None

def test_add_in_game_book_to_library():
    # Use a temp directory for save file
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = os.path.join(tmpdir, 'test_save.json')
        sim = get_simulator(save_path)
        # Simulate in-game books present in assets/books
        # We'll mock _scan_in_game_books to return a fake book
        fake_book = {
            "id": "test-book-id",
            "type": "in_game",
            "title": "Test Book",
            "source": "/fake/path/test-book.md"
        }
        sim._scan_in_game_books = lambda: [fake_book]
        # Add the book to the library
        sim.add_in_game_book_to_library("test-book-id")
        books = sim.get_library_books()
    assert any(b["id"] == "test-book-id" for b in books), f"Book should be in library order, got {[b['title'] for b in books]}"

def reset_simulator_singleton():
    # Remove the singleton instance from sys.modules and core_simulator
    import core_simulator
    if hasattr(core_simulator, '_simulator_instance'):
        del core_simulator._simulator_instance
    importlib.invalidate_caches()
    importlib.reload(core_simulator)

def test_add_in_game_book_to_library():
    reset_simulator_singleton()
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = os.path.join(tmpdir, 'test_save.json')
        import core_simulator
        sim = core_simulator.get_simulator(save_path)
        print(f"[TEST DEBUG] sim id: {id(sim)} get_simulator() id: {id(core_simulator.get_simulator())}")
        fake_book = {
            "id": "test-book-id",
            "type": "in_game",
            "title": "Test Book",
            "source": "/fake/path/test-book.md"
        }
        sim._scan_in_game_books = lambda: [fake_book]
        sim.add_in_game_book_to_library("test-book-id")
        books = sim.get_library_books()
    print("[TEST DEBUG] Library books after add:", books)
    print("[TEST DEBUG] Library order:", getattr(sim, 'library_order', None))
    print("[TEST DEBUG] sim.__dict__ after add:", sim.__dict__)
    assert any(b["id"] == "test-book-id" for b in books), f"Book should be in library order, got {[b['title'] for b in books]}"
    sim.remove_in_game_book_from_library("test-book-id")
    books = sim.get_library_books()
    print("[TEST DEBUG] Library books after remove:", books)
    assert not any(b["id"] == "test-book-id" for b in books), "Book should be removed from library order"

def test_user_books_are_loaded():
    reset_simulator_singleton()
    with tempfile.TemporaryDirectory() as tmpdir:
        books_dir = os.path.join(tmpdir, "AirshipZero", "books")
        os.makedirs(books_dir)
        book_path = os.path.join(books_dir, "userbook.md")
        with open(book_path, "w") as f:
            f.write("# User Book\nContent")
        import core_simulator
        sim = core_simulator.get_simulator(os.path.join(tmpdir, 'test_save.json'))
        print(f"[TEST DEBUG] sim id: {id(sim)} get_simulator() id: {id(core_simulator.get_simulator())}")
        from pathlib import Path
        sim._get_user_books_dir = lambda: Path(books_dir)
        sim.refresh_library_books()
        books = sim.get_library_books()
    print("[TEST DEBUG] User books after refresh:", books)
    print("[TEST DEBUG] Library order:", getattr(sim, 'library_order', None))
    print("[TEST DEBUG] sim.__dict__ after refresh:", sim.__dict__)
    assert any(b["type"] == "user" and b["title"].startswith("Userbook") for b in books), f"User book should be loaded from disk, got {[b['title'] for b in books]}"
