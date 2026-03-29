#!/usr/bin/env python3
"""Build script - Use PyInstaller to create Windows executable"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"Cleaning directory: {dir_path}")
            shutil.rmtree(dir_path)

    # Clean .spec file
    spec_file = Path("PDFConcat.spec")
    if spec_file.exists():
        spec_file.unlink()


def install_dependencies():
    """Install dependencies needed for packaging"""
    print("Installing packaging dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)


def build_executable():
    """Build using PyInstaller"""
    print("\nStarting build process...")

    # PyInstaller command parameters
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "PDFConcat",
        "--onefile",  # Package into single file
        "--windowed",  # Hide console window
        "--icon=NONE",  # Icon file (set to NONE if no icon)
        "--add-data", "src;src",  # Include src directory
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.filedialog",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "PIL",
        "--hidden-import", "fitz",
        "--hidden-import", "numpy",
        "src/gui.py"  # Entry file
    ]

    # If there is an icon file, uncomment and modify the path below
    # cmd.extend(["--icon", "assets/icon.ico"])

    # Run build command
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n[Success] Build completed successfully!")
        print(f"Executable file located at: {Path('dist/PDFConcat.exe').absolute()}")

        # Create portable package
        create_portable_package()
    else:
        print("\n[Error] Build failed!")
        sys.exit(1)


def create_portable_package():
    """Create portable package"""
    portable_dir = Path("PDFConcat_Portable")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)

    portable_dir.mkdir()

    # Copy executable file
    exe_path = Path("dist/PDFConcat.exe")
    shutil.copy2(exe_path, portable_dir)

    # Create example files and documentation
    create_readme(portable_dir)

    print(f"\n[Success] Portable version created: {portable_dir.absolute()}")


def create_readme(output_dir: Path):
    """Create documentation"""
    readme_content = """# PDFConcat v0.9.9

## Description
This is an easy-to-use Windows desktop application that creates thumbnail grids from PDF pages and arranges them in a new PDF file with customizable grid layouts.

## Main Features
- 🖱️ Intuitive graphical interface with drag-and-drop support
- 📐 Flexible grid layout configuration (custom rows and columns)
- 📄 Multiple paper size support (A4, A3, A5, Letter)
- 🔄 Landscape/portrait orientation toggle
- 🎨 Adjustable output quality (DPI, spacing, margins)
- ⚡ Quick preset configurations
- 📊 Real-time progress display

## How to Use

1. **Select Files**
   - Click the "Browse..." button to select input PDF files
   - Choose output file location (the program will suggest a filename automatically)
   - Or drag and drop PDF files directly into the input box

2. **Configure Parameters**
   - Set grid columns and rows
   - Select paper size and orientation
   - Adjust DPI (recommended 150-300)
   - Set thumbnail spacing and margins

3. **Start Processing**
   - Click the "Start Processing" button
   - Wait for the progress bar to complete
   - After processing, click "Open Output File" to view the result

## Quick Presets
- **A4 Landscape 3×2**: Suitable for arranging 3 columns and 2 rows on A4 paper in landscape
- **A4 Landscape 4×3**: Suitable for arranging 4 columns and 3 rows on A4 paper in landscape
- **A3 Landscape 5×3**: Suitable for arranging 5 columns and 3 rows on A3 paper in landscape
- **Auto Layout**: Program automatically calculates the most suitable layout

## Parameter Description

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| Columns | Number of thumbnails per row | 3 | 1-10 |
| Rows | Number of thumbnails per column | 2 | 1-10 |
| Paper Size | Output PDF paper size | Auto | A3/A4/A5/Letter |
| Orientation | Page orientation | Landscape | Landscape/Portrait |
| DPI | Output resolution | 150 | 50-600 |
| Spacing | Space between thumbnails (points) | 3 | 0-20 |
| Margin | Page edge whitespace (points) | 10 | 0-50 |

## Tips
- Click "Auto Calculate Rows" to automatically calculate the required rows based on PDF page count
- Use presets for quick configuration of common layouts
- Higher DPI will produce clearer output but also increase file size

## System Requirements
- Windows 7/8/10/11 (64-bit)
- No additional dependencies required (portable version)

## Change Log
v0.9.9 (2024-12-10)
- Beta version release
- Support for basic PDF grid concatenation functionality
- Graphical user interface
- Multiple configuration options

## Technical Support
For questions or suggestions, please contact: [your email]

---

The program is developed based on Python, using PyMuPDF for PDF processing.
"""

    readme_path = output_dir / "README.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    # Create an example batch file for quick launching
    bat_content = """@echo off
echo Starting PDFConcat...
start "" "PDFConcat.exe"
"""
    bat_path = output_dir / "Launch Program.bat"
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)


def main():
    print("=" * 50)
    print("PDFConcat - Build Script")
    print("=" * 50)

    # Check if in the correct directory
    if not Path("src/gui.py").exists():
        print("[Error] Please run this script from the project root directory")
        sys.exit(1)

    # Clean previous builds
    clean_build_dirs()

    # Install dependencies
    install_dependencies()

    # Build
    build_executable()

    print("\n" + "=" * 50)
    print("Build complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()