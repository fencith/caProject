@echo off
echo 🏗️ 开始构建南网E文件解析工具 (PySide6版本)...
echo.

python build_qt_app_v2.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ 构建完成!
    echo.
    echo 安装程序文件: installer\E文件解析工具_PySide6_Setup.exe
    echo 可执行文件: dist\E文件解析工具_PySide6\E文件解析工具_PySide6.exe
    echo.
    pause
) else (
    echo.
    echo ❌ 构建失败!
    echo.
    pause
)
