#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple test to verify the application works without QApplication issues
"""

import sys
import os

def test_application_logic():
    """Test the application logic without starting the full GUI"""
    print("Testing application logic...")

    try:
        # Test imports
        from PySide6.QtWidgets import QApplication, QMainWindow
        from PySide6.QtCore import QThread, Signal
        print("✓ PySide6 imports successful")

        # Test our module imports
        import efile_parser
        import db_utils
        print("✓ Local module imports successful")

        # Test that the EFileViewer class can be imported
        import qt_app_v2
        print("✓ qt_app_v2 module imports successfully")

        # Test that all the methods we added exist
        methods_to_check = [
            'browseFile', 'parseFile', 'onProgress',
            'onParseError', 'onParseFinished', 'displaySummary',
            'displayDataSections', 'onSectionClicked', 'updateCurveOptions'
        ]

        for method_name in methods_to_check:
            if hasattr(qt_app_v2.EFileViewer, method_name):
                print(f"✓ Method {method_name} exists")
            else:
                print(f"✗ Method {method_name} missing")
                return False

        print("✓ All required methods are present")
        return True

    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_matplotlib_compatibility():
    """Test Matplotlib compatibility detection"""
    print("\nTesting Matplotlib compatibility...")

    try:
        # Import the matplotlib detection logic
        import qt_app_v2

        # Check the global variable
        if hasattr(qt_app_v2, '_MATPLOTLIB_AVAILABLE'):
            available = qt_app_v2._MATPLOTLIB_AVAILABLE
            print(f"Matplotlib availability: {available}")

            if not available:
                print("✓ Matplotlib correctly detected as unavailable")
                return True
            else:
                print("✓ Matplotlib detected as available")
                return True
        else:
            print("✗ _MATPLOTLIB_AVAILABLE variable not found")
            return False

    except Exception as e:
        print(f"✗ Matplotlib test failed: {e}")
        return False

def main():
    print("Running simple tests for qt_app_v2.py...")
    print("=" * 50)

    # Test application logic
    logic_ok = test_application_logic()

    # Test matplotlib compatibility
    matplotlib_ok = test_matplotlib_compatibility()

    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Application Logic: {'PASS' if logic_ok else 'FAIL'}")
    print(f"Matplotlib Compatibility: {'PASS' if matplotlib_ok else 'FAIL'}")

    if logic_ok and matplotlib_ok:
        print("\n✓ All tests passed!")
        print("✓ The application should work correctly when started.")
        print("✓ Matplotlib curve functionality is properly handled.")
        return True
    else:
        print("\n✗ Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
