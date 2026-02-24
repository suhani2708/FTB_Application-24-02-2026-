import os
import sys
from pathlib import Path

print("=== FILE PATH DEBUGGING ===")

# Get base directory like the app does
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
    print(f"Running as executable, BASE_DIR: {BASE_DIR}")
else:
    BASE_DIR = Path(__file__).parent
    print(f"Running as script, BASE_DIR: {BASE_DIR}")

modules_path = BASE_DIR / "modules"
print(f"Modules path: {modules_path}")
print(f"Modules path exists: {modules_path.exists()}")

pptx_file = modules_path / "User_Guide.pptx"
print(f"PowerPoint file path: {pptx_file}")
print(f"PowerPoint file exists: {pptx_file.exists()}")

if modules_path.exists():
    files = list(modules_path.iterdir())
    print(f"Files in modules directory: {[f.name for f in files]}")

print("=== END DEBUGGING ===")