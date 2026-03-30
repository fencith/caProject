#!/usr/bin/env python3
"""
cx_Freeze setup script for EFileParser application
"""

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["PySide6", "sqlite3", "os", "sys", "datetime", "re", "json", "threading", "time", "glob", "shutil", "pathlib"],
    "excludes": ["tkinter"],
    "include_files": [
        "spic_logo.png",
        "spic_icon.ico",
        "南网102-e文件解析工具.spec",
        "qt_app_v2_restored.py",
        "efile_parser.py",
        "db_utils.py"
    ],
    "include_msvcr": True,
    "optimize": 2
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "gui"

executables = [
    Executable(
        "qt_app_v2_restored.py",
        base=base,
        target_name="EFileParser.exe",
        icon="spic_icon.ico",
        copyright="Copyright (C) 2026 SPIC",
        trademarks="EFileParser"
    )
]

setup(
    name="EFileParser",
    version="1.0.0",
    description="南方电网102规约E文件解析工具",
    options={"build_exe": build_exe_options},
    executables=executables
)