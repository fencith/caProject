@echo off
echo Creating installation package for qt_app_v2_restored...

:: Create installer directory if it doesn't exist
if not exist "installer" mkdir "installer"

:: Create a ZIP package
set PACKAGE_NAME=南网102-e文件解析工具_v2.1.2_Portable.zip
set TEMP_DIR=temp_package

echo Creating portable ZIP package: %PACKAGE_NAME%...

:: Clean up any existing temp directory
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"

:: Create temp directory
mkdir "%TEMP_DIR%"

:: Copy all necessary files
copy "dist\qt_app_v2_restored.exe" "%TEMP_DIR%\" >nul
copy "spic_logo.png" "%TEMP_DIR%\" >nul
copy "spic_icon.ico" "%TEMP_DIR%\" >nul

:: Create a README file
echo 南网102-e文件解析工具 v2.1.2 > "%TEMP_DIR%\README.txt"
echo. >> "%TEMP_DIR%\README.txt"
echo 国家电投云南国际  昆明生产运营中心 版权所有 >> "%TEMP_DIR%\README.txt"
echo. >> "%TEMP_DIR%\README.txt"
echo 安装说明: >> "%TEMP_DIR%\README.txt"
echo 1. 解压所有文件到同一目录 >> "%TEMP_DIR%\README.txt"
echo 2. 运行 qt_app_v2_restored.exe 启动应用程序 >> "%TEMP_DIR%\README.txt"
echo 3. 确保 spic_logo.png 和 spic_icon.ico 与可执行文件在同一目录 >> "%TEMP_DIR%\README.txt"
echo. >> "%TEMP_DIR%\README.txt"
echo 联系方式: 陈丰 电话: 0871-65666603 >> "%TEMP_DIR%\README.txt"

:: Create ZIP package
powershell -command "Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath 'installer\%PACKAGE_NAME%' -Force"

:: Clean up temp directory
rmdir /s /q "%TEMP_DIR%"

echo Portable ZIP package created successfully: installer\%PACKAGE_NAME%

:: Also copy the standalone executable to installer directory
copy "dist\qt_app_v2_restored.exe" "installer\南网102-e文件解析工具_v2.1.2.exe" >nul

echo Standalone executable copied to: installer\南网102-e文件解析工具_v2.1.2.exe

echo.
echo Installation package creation completed!
echo.
echo Available packages:
echo 1. Portable ZIP: installer\%PACKAGE_NAME% (includes all files)
echo 2. Standalone EXE: installer\南网102-e文件解析工具_v2.1.2.exe (requires manual resource file placement)
echo 3. Inno Setup script: qt_app_v2_restored_installer.iss (for creating MSI installer)
echo.
echo Note: For full functionality, ensure spic_logo.png and spic_icon.ico are in the same directory as the executable.
<task_progress>
- [x] Analyze the application structure
- [x] Check for existing build scripts
- [x] Create installation package with PyInstaller
- [x] Include spic_logo.png and spic_icon.ico
- [x] Test the installation package
</task_progress>
</write_to_file>