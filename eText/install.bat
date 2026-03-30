@echo off
chcp 65001 >nul
echo ============================================
echo E文件解析工具 v2.0.0 安装程序
echo ============================================
echo.

echo 正在安装 E文件解析工具...
echo.

REM 创建安装目录
if not exist "C:\Program Files\E文件解析工具" mkdir "C:\Program Files\E文件解析工具"

REM 复制文件
echo 复制程序文件...
copy "dist\eFileParser_v2.exe" "C:\Program Files\E文件解析工具\" >nul
copy "spic_logo.png" "C:\Program Files\E文件解析工具\" >nul
copy "eparser.db" "C:\Program Files\E文件解析工具\" >nul 2>nul
copy "README.md" "C:\Program Files\E文件解析工具\" >nul
copy "使用说明.md" "C:\Program Files\E文件解析工具\" >nul

REM 创建桌面快捷方式
echo 创建桌面快捷方式...
powershell "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%USERPROFILE%\Desktop\E文件解析工具.lnk'); $sc.TargetPath = 'C:\Program Files\E文件解析工具\eFileParser_v2.exe'; $sc.WorkingDirectory = 'C:\Program Files\E文件解析工具'; $sc.IconLocation = 'C:\Program Files\E文件解析工具\eFileParser_v2.exe'; $sc.Save()"

REM 创建开始菜单快捷方式
echo 创建开始菜单快捷方式...
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\E文件解析工具" mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\E文件解析工具"
powershell "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\E文件解析工具\E文件解析工具.lnk'); $sc.TargetPath = 'C:\Program Files\E文件解析工具\eFileParser_v2.exe'; $sc.WorkingDirectory = 'C:\Program Files\E文件解析工具'; $sc.IconLocation = 'C:\Program Files\E文件解析工具\eFileParser_v2.exe'; $sc.Save()"

powershell "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\E文件解析工具\卸载.lnk'); $sc.TargetPath = '%~dp0uninstall.bat'; $sc.WorkingDirectory = '%~dp0'; $sc.Save()"

echo.
echo ============================================
echo 安装完成！
echo ============================================
echo.
echo 程序已安装到: C:\Program Files\E文件解析工具
echo 桌面和开始菜单中已创建快捷方式
echo.
echo 按任意键启动程序...
pause >nul

REM 启动程序
start "" "C:\Program Files\E文件解析工具\eFileParser_v2.exe"

echo.
echo 安装完成！