@echo off
echo ============================================
echo E文件解析工具 - 打包为EXE
echo ============================================
echo.

echo 正在清理旧的打包文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

echo 正在打包应用...
pyinstaller --name="EFileParser" ^
    --windowed ^
    --icon=NONE ^
    --add-data="efile_parser.py;." ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=re ^
    qt_app.py

echo.
if exist dist\EFileParser.exe (
    echo ============================================
    echo 打包成功！
    echo ============================================
    echo.
    echo 可执行文件位置: dist\EFileParser.exe
    echo.
    echo 正在测试运行...
    start "" dist\EFileParser.exe
) else (
    echo 打包失败！请检查错误信息。
    echo.

echo.
pause
