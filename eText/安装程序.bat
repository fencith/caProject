@echo off
echo.
echo ================================
echo   E文件解析工具 (优化版) 安装程序
echo ================================
echo.
echo 版本: 2.1.3
echo 制造商: 国家电投云南国际
echo.
echo 此安装程序将把文件复制到 Program Files 目录。
echo.
pause

echo.
echo 正在创建安装目录...
set "INSTALL_DIR=%ProgramFiles%\E文件解析工具"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo 正在复制文件...
xcopy /E /I /Y "源代码" "%INSTALL_DIR%\源代码"
xcopy /E /I /Y "资源文件" "%INSTALL_DIR%\资源文件"
xcopy /E /I /Y "文档" "%INSTALL_DIR%\文档"
xcopy /E /I /Y "示例数据" "%INSTALL_DIR%\示例数据"
copy /Y "快速启动.bat" "%INSTALL_DIR%"
copy /Y "安装指南.md" "%INSTALL_DIR%"

echo.
echo 创建快捷方式...
set "SHORTCUT_DIR=%ProgramData%\Microsoft\Windows\Start Menu\Programs\E文件解析工具"
if not exist "%SHORTCUT_DIR%" mkdir "%SHORTCUT_DIR%"

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%SHORTCUT_DIR%\E文件解析工具.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\源代码\qt_app_v2_optimized_final.py" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%\源代码" >> CreateShortcut.vbs
echo oLink.IconLocation = "%INSTALL_DIR%\资源文件\spic_icon.ico" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut2.vbs
echo sLinkFile = "%SHORTCUT_DIR%\快速启动.lnk" >> CreateShortcut2.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut2.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\快速启动.bat" >> CreateShortcut2.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut2.vbs
echo oLink.Save >> CreateShortcut2.vbs
cscript CreateShortcut2.vbs
del CreateShortcut2.vbs

echo.
echo 创建桌面快捷方式...
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateDesktopShortcut.vbs
echo sLinkFile = "%DESKTOP_DIR%\E文件解析工具.lnk" >> CreateDesktopShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateDesktopShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\源代码\qt_app_v2_optimized_final.py" >> CreateDesktopShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%\源代码" >> CreateDesktopShortcut.vbs
echo oLink.IconLocation = "%INSTALL_DIR%\资源文件\spic_icon.ico" >> CreateDesktopShortcut.vbs
echo oLink.Save >> CreateDesktopShortcut.vbs
cscript CreateDesktopShortcut.vbs
del CreateDesktopShortcut.vbs

echo.
echo 安装完成！
echo.
echo 安装位置: %INSTALL_DIR%
echo.
echo 使用方法:
echo 1. 双击桌面上的快捷方式
echo 2. 或者运行开始菜单中的程序
echo 3. 首次使用前请安装 Python 依赖:
echo    cd "%INSTALL_DIR%\源代码"
echo    pip install -r requirements_optimized.txt
echo.
echo 请按任意键退出...
pause >nul
