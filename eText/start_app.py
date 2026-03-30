#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Clean startup script for qt_app_v2.py that handles QApplication singleton issues
"""

import sys
import os
import time
import subprocess

def main():
    print("Starting E文件解析工具 v2.0.0...")
    print("国家电投昆明生产运营中心 版权所有")
    print("=" * 50)

    try:
        # Start the application in a new process to avoid singleton issues
        process = subprocess.Popen(
            [sys.executable, "qt_app_v2.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        print("✓ Application started successfully")
        print("✓ Process ID:", process.pid)
        print("✓ The application window should appear shortly")

        # Give it a moment to start
        time.sleep(2)

        # Check if process is still running
        if process.poll() is None:
            print("✓ Application is running")
            print("✓ You can now use the E文件解析工具")
        else:
            stdout, stderr = process.communicate()
            print("✗ Application failed to start:")
            print("STDOUT:", stdout)
            print("STDERR:", stderr)

    except Exception as e:
        print(f"✗ Failed to start application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
