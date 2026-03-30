#!/usr/bin/env python3
"""
PyInstaller build script for qt_app_v2.py
Creates a standalone Windows executable for the E文件解析工具
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    app_file = script_dir / "qt_app_v2.py"
    
    if not app_file.exists():
        print(f"Error: {app_file} not found!")
        sys.exit(1)
    
    # Build command with PyInstaller
    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=南网102-e文件解析工具",
        "--windowed",  # GUI application, no console
        "--onefile",   # Single executable
        "--clean",     # Clean PyInstaller cache
        "--icon=spic_icon.ico",  # Use the SPIC icon
        "--add-data=spic_icon.ico;.",  # Include icon in the executable
        "--hidden-import=sqlite3",
        "--hidden-import=winreg",
        "--hidden-import=tarfile",
        "--hidden-import=tempfile",
        "--hidden-import=shutil",
        "--hidden-import=datetime",
        "--hidden-import=json",
        "--hidden-import=PySide6",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=efile_parser",
        "--hidden-import=db_utils",
        str(app_file)
    ]
    
    print("Building Windows executable...")
    print("Command:", " ".join(build_cmd))
    print("-" * 50)
    
    try:
        # Run the build command
        result = subprocess.run(build_cmd, cwd=script_dir, check=True)
        
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("✅ Build successful!")
            print(f"Executable created in: {script_dir / 'dist' / '南网102-e文件解析工具.exe'}")
            print("=" * 50)
        else:
            print(f"\n❌ Build failed with return code: {result.returncode}")
            sys.exit(result.returncode)
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()