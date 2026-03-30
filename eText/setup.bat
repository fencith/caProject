@echo off
echo.
echo ================================
echo   E文件解析工具 (优化版) 安装程序
echo ================================
echo.
echo 版本: 2.1.3
echo 制造商: 国家电投云南国际
echo.
echo 此安装程序将把文件复制到指定目录。
echo.
pause

echo.
echo 请输入安装目录 (默认: C:\Program Files\E文件解析工具):
set /p INSTALL_DIR=安装目录: 

if "%INSTALL_DIR%"=="" set INSTALL_DIR=C:\Program Files\E文件解析工具

echo.
echo 安装目录: %INSTALL_DIR%
echo.
echo 确认安装? (y/n)
set /p CONFIRM=确认: 

if /i "%CONFIRM%" neq "y" (
    echo 安装已取消
    pause
    exit /b
)

echo.
echo 正在创建安装目录...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo 正在创建子目录...
mkdir "%INSTALL_DIR%\源代码" 2>nul
mkdir "%INSTALL_DIR%\资源文件" 2>nul
mkdir "%INSTALL_DIR%\文档" 2>nul
mkdir "%INSTALL_DIR%\示例数据" 2>nul

echo.
echo 正在复制文件...

echo   复制源代码文件...
copy /Y "qt_app_v2_optimized_final.py" "%INSTALL_DIR%\源代码\" >nul
copy /Y "efile_parser_optimized.py" "%INSTALL_DIR%\源代码\" >nul
copy /Y "db_utils_optimized.py" "%INSTALL_DIR%\源代码\" >nul
copy /Y "requirements_optimized.txt" "%INSTALL_DIR%\源代码\" >nul
copy /Y "build_qt_app_v2_optimized.py" "%INSTALL_DIR%\源代码\" >nul

echo   复制资源文件...
copy /Y "spic_icon.ico" "%INSTALL_DIR%\资源文件\" >nul
copy /Y "spic_logo.png" "%INSTALL_DIR%\资源文件\" >nul

echo   复制文档文件...
copy /Y "README.md" "%INSTALL_DIR%\文档\" >nul

echo   复制示例数据...
copy /Y "102E2601\FD_YN.HongTPDC_TJXX_20260102_193000.dat" "%INSTALL_DIR%\示例数据\" >nul
copy /Y "102E2601\FD_YN.HongTPDC_CDQYC_20260114_163000.dat" "%INSTALL_DIR%\示例数据\" >nul
copy /Y "102E2601\FD_YN.HongTPDC_FDJZ_20260114_163000.dat" "%INSTALL_DIR%\示例数据\" >nul

echo.
echo 创建安装指南...
echo # E文件解析工具 安装指南> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ## 版本信息>> "%INSTALL_DIR%\安装指南.md"
echo - 版本: 2.1.3>> "%INSTALL_DIR%\安装指南.md"
echo - 发布时间: %date%>> "%INSTALL_DIR%\安装指南.md"
echo - 制造商: 国家电投云南国际>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ## 安装步骤>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ### 1. 运行安装程序>> "%INSTALL_DIR%\安装指南.md"
echo 双击 setup.exe 文件开始安装。>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ### 2. 选择安装位置>> "%INSTALL_DIR%\安装指南.md"
echo 安装程序会提示您选择安装目录。>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ### 3. 完成安装>> "%INSTALL_DIR%\安装指南.md"
echo 安装完成后，您可以在以下位置找到应用程序：>> "%INSTALL_DIR%\安装指南.md"
echo - 开始菜单: E文件解析工具>> "%INSTALL_DIR%\安装指南.md"
echo - 桌面: E文件解析工具 快捷方式（可选）>> "%INSTALL_DIR%\安装指南.md"
echo - 安装目录: 源代码\qt_app_v2_optimized_final.py>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ## 使用方法>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ### 1. 安装 Python 依赖>> "%INSTALL_DIR%\安装指南.md"
echo 首次使用前，请安装必要的 Python 依赖：>> "%INSTALL_DIR%\安装指南.md"
echo ```bash>> "%INSTALL_DIR%\安装指南.md"
echo cd "安装目录\源代码">> "%INSTALL_DIR%\安装指南.md"
echo pip install -r requirements_optimized.txt>> "%INSTALL_DIR%\安装指南.md"
echo ```>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ### 2. 运行应用程序>> "%INSTALL_DIR%\安装指南.md"
echo ```bash>> "%INSTALL_DIR%\安装指南.md"
echo cd "安装目录\源代码">> "%INSTALL_DIR%\安装指南.md"
echo python qt_app_v2_optimized_final.py>> "%INSTALL_DIR%\安装指南.md"
echo ```>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ## 包含文件>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ### 源代码>> "%INSTALL_DIR%\安装指南.md"
echo - qt_app_v2_optimized_final.py - 主应用程序>> "%INSTALL_DIR%\安装指南.md"
echo - efile_parser_optimized.py - E文件解析器>> "%INSTALL_DIR%\安装指南.md"
echo - db_utils_optimized.py - 数据库工具>> "%INSTALL_DIR%\安装指南.md"
echo - requirements_optimized.txt - 依赖列表>> "%INSTALL_DIR%\安装指南.md"
echo - build_qt_app_v2_optimized.py - 构建脚本>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ### 资源文件>> "%INSTALL_DIR%\安装指南.md"
echo - spic_icon.ico - 应用图标>> "%INSTALL_DIR%\安装指南.md"
echo - spic_logo.png - SPIC Logo>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ### 文档>> "%INSTALL_DIR%\安装指南.md"
echo - README.md - 项目说明>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ### 示例数据>> "%INSTALL_DIR%\安装指南.md"
echo 包含用于测试的示例 E文件>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ## 系统要求>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo - Windows 7 SP1 或更高版本>> "%INSTALL_DIR%\安装指南.md"
echo - Python 3.8 或更高版本（运行时需要）>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ## 技术支持>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo 如有问题，请联系：>> "%INSTALL_DIR%\安装指南.md"
echo - 开发者: 陈丰>> "%INSTALL_DIR%\安装指南.md"
echo - 电话: 0871-65666603>> "%INSTALL_DIR%\安装指南.md"
echo - 单位: 国家电投云南国际 昆明生产运营中心>> "%INSTALL_DIR%\安装指南.md"
echo.>> "%INSTALL_DIR%\安装指南.md"
echo ## 版权信息>> "%INSTALL_DIR%\安装指南.md"
echo © %date:~0,4% 国家电投云南国际 版权所有>> "%INSTALL_DIR%\安装指南.md"

echo.
echo 创建快速启动脚本...
echo @echo off> "%INSTALL_DIR%\快速启动.bat"
echo echo.>> "%INSTALL_DIR%\快速启动.bat"
echo echo ================================>> "%INSTALL_DIR%\快速启动.bat"
echo echo   E文件解析工具 快速启动>> "%INSTALL_DIR%\快速启动.bat"
echo echo ================================>> "%INSTALL_DIR%\快速启动.bat"
echo echo.>> "%INSTALL_DIR%\快速启动.bat"
echo echo 1. 运行源代码版本>> "%INSTALL_DIR%\快速启动.bat"
echo echo 2. 构建可执行文件>> "%INSTALL_DIR%\快速启动.bat"
echo echo 3. 查看安装指南>> "%INSTALL_DIR%\快速启动.bat"
echo echo 4. 退出>> "%INSTALL_DIR%\快速启动.bat"
echo echo.>> "%INSTALL_DIR%\快速启动.bat"
echo set /p choice=请选择操作 (1-4): >> "%INSTALL_DIR%\快速启动.bat"
echo.>> "%INSTALL_DIR%\快速启动.bat"
echo if "%%choice%%"=="1" goto run_source>> "%INSTALL_DIR%\快速启动.bat"
echo if "%%choice%%"=="2" goto build_exe>> "%INSTALL_DIR%\快速启动.bat"
echo if "%%choice%%"=="3" goto view_guide>> "%INSTALL_DIR%\快速启动.bat"
echo if "%%choice%%"=="4" goto exit_script>> "%INSTALL_DIR%\快速启动.bat"
echo.>> "%INSTALL_DIR%\快速启动.bat"
echo :run_source>> "%INSTALL_DIR%\快速启动.bat"
echo echo.>> "%INSTALL_DIR%\快速启动.bat"
echo echo 正在启动源代码版本...>> "%INSTALL_DIR%\快速启动.bat"
echo cd "源代码">> "%INSTALL_DIR%\快速启动.bat"
echo python qt_app_v2_optimized_final.py>> "%INSTALL_DIR%\快速启动.bat"
echo goto end>> "%INSTALL_DIR%\快速启动.bat"
echo.>> "%INSTALL_DIR%\快速启动.bat"
echo :build_exe>> "%INSTALL_DIR%\快速启动.bat"
echo echo.>> "%INSTALL_DIR%\快速启动.bat"
echo echo 正在构建可执行文件...>> "%INSTALL_DIR%\快速启动.bat"
echo cd "源代码">> "%INSTALL_DIR%\快速启动.bat"
echo python build_qt_app_v2_optimized.py>> "%INSTALL_DIR%\快速启动.bat"
echo echo.>> "%INSTALL_DIR%\快速启动.bat"
echo echo 构建完成！可执行文件在 dist 目录中。>> "%INSTALL_DIR%\快速启动.bat"
echo pause>> "%INSTALL_DIR%\快速启动.bat"
echo goto end>> "%INSTALL_DIR%\快速启动.bat"
echo.>> "%INSTALL_DIR%\快速启动.bat"
echo :view_guide>> "%INSTALL_DIR%\快速启动.bat"
echo echo.>> "%INSTALL_DIR%\快速启动.bat"
echo echo 正在打开安装指南...>> "%INSTALL_DIR%\快速启动.bat"
echo start "" "安装指南.md">> "%INSTALL_DIR%\快速启动.bat"
echo goto end>> "%INSTALL_DIR%\快速启动.bat"
echo.>> "%INSTALL_DIR%\快速启动.bat"
echo :exit_script>> "%INSTALL_DIR%\快速启动.bat"
echo echo.>> "%INSTALL_DIR%\快速启动.bat"
echo echo 感谢使用！>> "%INSTALL_DIR%\快速启动.bat"
echo goto end>> "%INSTALL_DIR%\快速启动.bat"
echo.>> "%INSTALL_DIR%\快速启动.bat"
echo :end>> "%INSTALL_DIR%\快速启动.bat"
echo echo.>> "%INSTALL_DIR%\快速启动.bat"
echo pause>> "%INSTALL_DIR%\快速启动.bat"

echo.
echo 创建快捷方式...
set "START_MENU_DIR=%ProgramData%\Microsoft\Windows\Start Menu\Programs\E文件解析工具"
if not exist "%START_MENU_DIR%" mkdir "%START_MENU_DIR%"

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%START_MENU_DIR%\E文件解析工具.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\源代码\qt_app_v2_optimized_final.py" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%\源代码" >> CreateShortcut.vbs
echo oLink.IconLocation = "%INSTALL_DIR%\资源文件\spic_icon.ico" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

echo Set oWS2 = WScript.CreateObject("WScript.Shell") >> CreateShortcut.vbs
echo sLinkFile2 = "%START_MENU_DIR%\快速启动.lnk" >> CreateShortcut.vbs
echo Set oLink2 = oWS2.CreateShortcut(sLinkFile2) >> CreateShortcut.vbs
echo oLink2.TargetPath = "%INSTALL_DIR%\快速启动.bat" >> CreateShortcut.vbs
echo oLink2.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
echo oLink2.Save >> CreateShortcut.vbs

echo Set oWS3 = WScript.CreateObject("WScript.Shell") >> CreateShortcut.vbs
echo sDesktopLink = "%USERPROFILE%\Desktop\E文件解析工具.lnk" >> CreateShortcut.vbs
echo Set oDesktopLink = oWS3.CreateShortcut(sDesktopLink) >> CreateShortcut.vbs
echo oDesktopLink.TargetPath = "%INSTALL_DIR%\源代码\qt_app_v2_optimized_final.py" >> CreateShortcut.vbs
echo oDesktopLink.WorkingDirectory = "%INSTALL_DIR%\源代码" >> CreateShortcut.vbs
echo oDesktopLink.IconLocation = "%INSTALL_DIR%\资源文件\spic_icon.ico" >> CreateShortcut.vbs
echo oDesktopLink.Save >> CreateShortcut.vbs

cscript CreateShortcut.vbs >nul
del CreateShortcut.vbs

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