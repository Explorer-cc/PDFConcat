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
- `src/gui.py` — `PDFConcatApp` class. tkinter GUI with threading for non-blocking processing. Imports `process_pdf` from the core module.
- `concat_pdf.py` / `run_gui.py` — Convenience launchers that add `src/` to `sys.path` and delegate to the core module's `main()` or the GUI respectively.
- `build.py` — PyInstaller build script. Creates a single-file Windows executable and a portable distribution folder.

## Key Dependencies

- **PyMuPDF** (`fitz`) — PDF rendering and manipulation
- **Pillow** — Image handling
- **NumPy** — Numerical operations
- **tkinter** — GUI (stdlib)
- Python >=3.12 required

## Important Rules

- **务必使用 `uv run` 执行所有 Python 运行任务**，不要直接用 `python` 命令。包括运行 GUI、CLI、测试等一切需要执行 Python 的场景。

## Important Details

- Page sizes in the codebase are in **points** (72 points = 1 inch). Standard sizes: A4=(595.276, 841.890), Letter=(612, 792).
- The GUI uses `sys.path.insert` to resolve imports from `src/` rather than an installed package. The `build.py` script uses `--add-data "src;src"` for PyInstaller to include the source.
- There are no tests, linter config, or CI setup currently.
