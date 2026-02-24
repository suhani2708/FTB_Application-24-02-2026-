#!/usr/bin/env python3
"""
Complete PyInstaller build script for EDU Toolbox
Ensures all assets are included in the executable
"""
import os
import sys
import shutil
from pathlib import Path
import PyInstaller.__main__

def build_executable():
    """Build the complete executable with all assets"""
    
    # Get current directory
    current_dir = Path(__file__).parent
    
    # Clean previous builds
    dist_dir = current_dir / "dist"
    build_dir = current_dir / "build"
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("Cleaned dist directory")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("Cleaned build directory")
    
    # Verify required directories exist
    required_dirs = ['ui', 'assets', 'modules', 'data', 'config']
    for dir_name in required_dirs:
        dir_path = current_dir / dir_name
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"Created missing directory: {dir_name}")
    
    # Build with PyInstaller
    PyInstaller.__main__.run([
        'app.py',
        '--name=EDU_Toolbox',
        '--onefile',
        '--windowed',
        '--add-data=ui;ui',
        '--add-data=assets;assets',
        '--add-data=modules;modules',
        '--add-data=data;data',
        '--add-data=config;config',
        '--hidden-import=webview',
        '--hidden-import=flask',
        '--hidden-import=sqlite3',
        '--clean',
        '--noconfirm'
    ])
    
    print("\n" + "="*50)
    print("BUILD COMPLETE!")
    print("="*50)
    print(f"Executable location: {dist_dir / 'EDU_Toolbox.exe'}")
    print("\nTo test the executable:")
    print("1. Copy the entire assets/ folder to the same directory as the .exe")
    print("2. Run the .exe file")
    print("3. All file paths will be resolved dynamically")

if __name__ == "__main__":
    build_executable()