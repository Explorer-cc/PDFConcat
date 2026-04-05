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


def build_executable():
    """Build using PyInstaller"""
    print("\nStarting build process...")

    # PyInstaller command parameters
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "PDFConcat",
        "--onefile",  # Package into single file
        "--windowed",  # Hide console window
        "--icon=icons/pdf-blue.ico",  # Blue icon for exe file
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
    else:
        print("\n[Error] Build failed!")
        sys.exit(1)


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

    # Build
    build_executable()

    print("\n" + "=" * 50)
    print("Build complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()