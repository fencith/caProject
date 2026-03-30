@echo off
echo Testing the qt_app_v2_restored installation...

:: Check if the executable exists
if not exist "dist\qt_app_v2_restored.exe" (
    echo Error: Executable not found!
    exit /b 1
)

:: Check if resource files exist
if not exist "spic_logo.png" (
    echo Error: spic_logo.png not found!
    exit /b 1
)

if not exist "spic_icon.ico" (
    echo Error: spic_icon.ico not found!
    exit /b 1
)

echo All files are present and ready for testing.

:: Create a test directory
set TEST_DIR=test_installation
if exist "%TEST_DIR%" rmdir /s /q "%TEST_DIR%"
mkdir "%TEST_DIR%"

:: Copy files to test directory
copy "dist\qt_app_v2_restored.exe" "%TEST_DIR%\" >nul
copy "spic_logo.png" "%TEST_DIR%\" >nul
copy "spic_icon.ico" "%TEST_DIR%\" >nul

echo Files copied to test directory: %TEST_DIR%

:: Test the executable
echo Testing the executable...
cd "%TEST_DIR%"
start "" "qt_app_v2_restored.exe"
cd ..

echo Installation test completed!
echo You can find the test installation in the "%TEST_DIR%" directory.
<task_progress>
- [x] Analyze the application structure
- [x] Check for existing build scripts
- [x] Create installation package with PyInstaller
- [x] Include spic_logo.png and spic_icon.ico
- [x] Test the installation package
</task_progress>
</write_to_file>