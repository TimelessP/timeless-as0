# Contributors & Developer Guide

Thank you for your interest in Airship Zero! This guide will help you get started as a contributor, understand the codebase, and follow our development practices.

---

## 🚦 Getting Started

1. **Fork this repository** on GitHub.
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/timeless-as0.git
   cd timeless-as0
   ```
3. **Install [UV](https://astral.sh/uv/)** (if you don't have it):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or see https://astral.sh/uv/ for Windows instructions
   ```
4. **Sync dependencies and set up the virtual environment:**
   ```bash
   uv sync
   ```
5. **Run the game in development mode:**
   ```bash
   ./run.sh
   # or
   uv run python main.py
   ```

---

## 🛠️ Directory Structure

- `main.py` — Entry point, scene management
- `core_simulator.py` — Central game state and physics
- `scene_*.py` — Each major game area is a separate scene (see below)
- `assets/` — Fonts, images, and in-game books (Markdown)
- `tests/` — Pytest-based tests
- `pyproject.toml` — Project config (dependencies, build, etc.)

---

## 🎬 Scene System

- Each `scene_*.py` file is a self-contained UI and logic module (e.g., `scene_bridge.py`, `scene_cargo.py`).
- Scenes handle their own widgets, rendering, and event logic.
- Scene transitions are managed by `main.py` via return values (e.g., `"scene_bridge"`, `"scene_main_menu"`).
- All game state is managed by the singleton in `core_simulator.py`—scenes are stateless except for UI.

---

## 🧑‍💻 Coding Style

- Use clear docstrings and type hints (`Optional`, `List`, `Dict` from `typing`).
- Constants (colors, sizes) go at the module level (`theme.py`).
- Use relative paths (from the current file path) for assets - do not change CWD.
- All state changes must go through `core_simulator.py`.
- Widget focus: Tab/Shift+Tab cycles focus; arrow keys are scene-specific.
- See `.github/copilot-instructions.md` for full guidelines.

---

## 🔄 Upgrading & Tooling

- **Upgrade your dev environment:**
  ```bash
  uv sync  # Update dependencies
  uv tool upgrade airshipzero  # If installed as a tool
  ```
- **Run tests:**
  ```bash
  uv run pytest
  ```
- **Check formatting:**
  ```bash
  uv run black .
  uv run ruff .
  ```
- **Run directly from a git repository URL:**
  ```bash
  uv tool run --from git+https://github.com/YOUR_USERNAME/timeless-as0 airshipzero
  ```

---

## 🧩 How UV & Upgrades Work

- UV manages all dependencies and virtual environments for you.
- When you install as a tool (`uv tool install ...`), you can run `airshipzero` from anywhere.
- To get the latest version:
  ```bash
  uv tool upgrade airshipzero
  ```
- For local development, always run `uv sync` after pulling new changes.

---

## 🤝 Contributing

- Fork, branch, and submit pull requests.
- Please keep PRs focused and small.
- Follow the coding style and scene/state patterns.
- All contributors are welcome—code, docs, art, or ideas!

---

Happy hacking, and welcome aboard!
