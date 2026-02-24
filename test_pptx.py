import os
import subprocess
from pathlib import Path

# Test PowerPoint file opening
pptx_file = Path("dist/modules/User_Guide.pptx")

print(f"File exists: {pptx_file.exists()}")
print(f"File path: {pptx_file.absolute()}")

if pptx_file.exists():
    try:
        print("Trying os.startfile...")
        os.startfile(str(pptx_file))
        print("os.startfile succeeded")
    except Exception as e:
        print(f"os.startfile failed: {e}")
        try:
            print("Trying subprocess...")
            subprocess.run(['start', '', str(pptx_file)], shell=True, check=False)
            print("subprocess succeeded")
        except Exception as e2:
            print(f"subprocess failed: {e2}")