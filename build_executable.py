"""
Build script to create executable using PyInstaller
"""
import os
import sys
import subprocess

def build_executable():
    """Build the desktop application executable"""
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                    # Single executable file
        '--windowed',                   # No console window
        '--name=EDU_Toolbox',          # Executable name
        '--icon=assets/icons/NividLogo.ico',  # Application icon
        '--add-data=ui;ui',            # Include UI folder
        '--add-data=assets;assets',    # Include assets folder
        '--hidden-import=webview',     # Ensure webview is included
        '--hidden-import=sqlite3',     # Ensure sqlite3 is included
        'app.py'                       # Main application file
    ]
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print("Executable created in 'dist' folder")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("PyInstaller not found. Install with: pip install pyinstaller")
        return False

if __name__ == '__main__':
    build_executable()