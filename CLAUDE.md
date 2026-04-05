# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDFConcat — a Python desktop app that arranges PDF pages into NxM thumbnail grids in a new PDF. Offers both a tkinter GUI and a CLI interface.

## Common Commands

```bash
# Install dependencies (uses uv package manager)
uv sync

# Run GUI
uv run src/gui.py

# Run CLI
uv run python concat_pdf.py input.pdf output.pdf -n 3 -m 2
uv run python concat_pdf.py input.pdf output.pdf -n 4 --page-size A4 --orientation landscape

# Build Windows executable (PyInstaller, outputs to dist/)
uv run python build.py
```

## Architecture

**Two-layer design:** core processing logic in `src/concat_pdf/` and GUI in `src/gui.py`.

- `src/concat_pdf/__init__.py` — Core module. `process_pdf()` is the main entry point. Uses PyMuPDF (fitz) to render PDF pages into grid layouts. `calculate_grid_size()` computes grid dimensions. Auto-calculates page size when none specified.
- `src/gui.py` — `PDFConcatApp` class. Custom undecorated window (`overrideredirect(True)`) with a hand-drawn title bar (Canvas buttons for min/max/close). Color palette centralized in the `COLORS` dict at module top. Uses `tkinterdnd2` for drag-and-drop and threading for non-blocking PDF processing.
- `concat_pdf.py` — CLI launcher. Adds `src/` to `sys.path` and delegates to `concat_pdf.main()`.
- `build.py` — PyInstaller build script. Creates a single-file Windows executable to `dist/PDFConcat.exe`. Requires `pyinstaller` installed as a dev dependency (`uv add pyinstaller --dev`). Uses blue icon (`icons/pdf-blue.ico`) for the exe. Cleans `build/`, `dist/`, and `.spec` files before each build.

## Key Dependencies

- **PyMuPDF** (`fitz`) — PDF rendering and manipulation
- **Pillow** — Image handling
- **NumPy** — Numerical operations
- **tkinter** — GUI (stdlib)
- **tkinterdnd2** — Drag-and-drop support for the GUI
- Python >=3.12 required

## Important Rules

- **务必使用 `uv run` 执行所有 Python 运行任务**，不要直接用 `python` 命令。包括运行 GUI、CLI、测试等一切需要执行 Python 的场景。
- **构建前需先安装 PyInstaller**: `uv add pyinstaller --dev`（`build.py` 不会自动安装依赖）。
- **Git 提交时不要添加 Claude 作为 contributor**，不要在 commit message 中附带 `Co-Authored-By` 行。

## Important Details

- Page sizes in the codebase are in **points** (72 points = 1 inch). Standard sizes: A4=(595.276, 841.890), Letter=(612, 792).
- The GUI uses `sys.path.insert` to resolve imports from `src/` rather than an installed package. The `build.py` script uses `--add-data "src;src"` for PyInstaller to include the source.
- GUI color theme is defined in the `COLORS` dict at the top of `src/gui.py`. Modify colors there, not inline. ttk styles are configured in `configure_styles()` at module bottom.
- The GUI window is undecorated (`overrideredirect(True)`) with a custom title bar drawn via `create_title_bar()`. The title bar uses Canvas widgets for pixel-precise min/max/close buttons.
- Window icon (title bar): `icons/pdf-red.ico`. Exe icon (build): `icons/pdf-blue.ico`.
- PDF processing runs in a background thread (`threading.Thread`) to keep the GUI responsive. Progress is reported back to the GUI via `root.after()` calls.
- `process_pdf()` in the core module uses `page.show_pdf_page()` (vector re-embedding) rather than rasterizing pages, which preserves quality and is more efficient.
- There are no tests, linter config, or CI setup currently.
