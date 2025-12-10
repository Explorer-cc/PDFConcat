# PDF Thumbnail Grid Tool

A lightweight Python tool that transforms PDF pages into organized thumbnail grids. Perfect for creating document previews, proofreading layouts, or compact document summaries.

## Features

- 🚀 **Smart Layout**: Automatically calculates optimal page size to minimize whitespace
- 🎛️ **Flexible Configuration**: Customizable grid dimensions (rows × columns)
- 🎨 **Quality Control**: Adjustable DPI for clear or compact thumbnails
- 🖥️ **User-Friendly GUI**: Intuitive interface with drag-and-drop support
- ⚡ **Quick Presets**: Pre-configured layouts for common use cases
- 📦 **Standalone Executable**: Windows .exe file requires no installation

## Quick Start

### For Windows Users (Recommended)

Download and run the standalone executable:

1. Navigate to `dist/PDF Thumbnail Grid Tool.exe` after building
2. Double-click to launch the GUI
3. Select your PDF file and configure your grid layout
4. Click "Start Processing" to generate thumbnails

### For Developers

#### Prerequisites
- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

#### Installation

```bash
# Clone the repository
git clone <repository-url>
cd concat_pdf

# Install dependencies
uv sync

# Optional: Install GUI dependencies for packaging
uv sync --extra gui
```

#### Running the Application

```bash
# GUI version
uv run src/gui.py

# Command-line version
uv run python -m concat_pdf input.pdf output.pdf -n 3
```

## Building the Executable

### Windows Executable

```bash
# Install packaging dependencies
uv sync --extra gui

# Build the .exe file
uv run pyinstaller --name "PDF Thumbnail Grid Tool" --onefile --windowed --add-data "src;src" src/gui.py

# The executable will be in the dist/ directory
```

### Portable Version

For a complete portable package with documentation:

```bash
# Run the build script (Windows only)
python build.py

# This creates:
# - dist/PDF Thumbnail Grid Tool.exe
# - PDF Thumbnail Grid Tool_Portable/ (with README and launcher)
```

## Usage Guide

### GUI Interface

1. **File Selection**
   - Use "Browse..." buttons or drag-and-drop PDF files
   - Output filename is auto-generated from input

2. **Grid Configuration**
   - **Columns**: Number of thumbnails per row (1-10)
   - **Rows**: Number of thumbnails per column (1-10)
   - **Auto Calculate Rows**: Automatically determine rows based on page count

3. **Quality Settings**
   - **DPI**: Resolution (50-600, recommended 150-300)
   - **Spacing**: Gap between thumbnails (0-20 points)
   - **Margin**: Page edge whitespace (0-50 points)

4. **Quick Presets**
   - 3×2 Grid: Standard 3 columns, 2 rows layout
   - 4×3 Grid: Denser layout with 4 columns, 3 rows
   - 5×3 Grid: Large format with 5 columns, 3 rows
   - Auto Layout: Intelligent layout based on content

### Command Line Interface

```bash
# Basic usage
uv run python -m concat_pdf input.pdf output.pdf -n 3

# Advanced options
uv run python -m concat_pdf input.pdf output.pdf \
    -n 4 \          # 4 columns
    -m 3 \          # 3 rows
    --dpi 200 \     # High quality
    --gap 2 \       # Small gaps
    --padding 5     # Minimal margins
```

## File Structure

```
concat_pdf/
├── src/
│   ├── gui.py              # GUI application
│   └── concat_pdf/
│       └── __init__.py     # Core processing logic
├── concat_pdf.py           # CLI entry point
├── build.py                # Build script for Windows
├── pyproject.toml          # Project configuration
├── README.md               # This file
├── .gitignore             # Git ignore rules
└── dist/                  # Build output directory
    └── PDF Thumbnail Grid Tool.exe
```

## Dependencies

- **PyMuPDF**: PDF processing and rendering
- **Pillow**: Image manipulation
- **NumPy**: Numerical operations
- **tkinter**: GUI framework (included with Python)

## Troubleshooting

### Common Issues

1. **"Cannot read PDF file"**
   - Ensure the PDF is not password-protected
   - Check if the file is corrupted

2. **Executable won't run**
   - Windows Defender may flag it - click "More info" → "Run anyway"
   - Ensure you're running on Windows 7/8/10/11 (64-bit)

3. **Large output file size**
   - Reduce DPI setting
   - Increase spacing between thumbnails

## License

This project is open source. See LICENSE file for details.

