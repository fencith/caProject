#!/usr/bin/env python3
"""
创建 PyNSIS 安装包
Create PyNSIS Installer
使用 pynsist 创建简单的 Windows 安装程序
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime


class PyNSISBuilder:
    """PyNSIS 安装包构建器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.app_name = "E文件解析工具"
        self.display_name = "E文件解析工具 (优化版)"
        self.version = "2.1.3"
        self.manufacturer = "国家电投云南国际"
        
        # 检查是否安装了 pynsist
        self.pynsist_available = self.check_pynsist()
        
        # 要包含的文件
        self.files_to_include = [
            ("qt_app_v2_optimized_final.py", "源代码"),
            ("efile_parser_optimized.py", "源代码"),
            ("db_utils_optimized.py", "源代码"),
            ("requirements_optimized.txt", "源代码"),
            ("build_qt_app_v2_optimized.py", "源代码"),
            ("spic_icon.ico", "资源文件"),
            ("spic_logo.png", "资源文件"),
            ("README.md", "文档"),
            ("南方电网新能源数据上送规范 V3.3修订版（2022.2月）.pdf", "文档"),
        ]
        
        # 示例数据文件
        self.sample_data_files = []
        self.collect_sample_data()
    
    def check_pynsist(self):
        """检查是否安装了 pynsist"""
        try:
            import pynsist
            print(f"✅ 找到 pynsist: {pynsist.__version__}")
            return True
        except ImportError:
            print("❌ 未找到 pynsist，请先安装: pip install pynsist")
            return False
    
    def collect_sample_data(self):
        """收集示例数据文件"""
        sample_data_dir = self.project_root / "102E2601"
        if sample_data_dir.exists():
            dat_files = list(sample_data_dir.glob("*.dat"))
            if dat_files:
                # 取最新的3个文件
                dat_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                self.sample_data_files = dat_files[:3]
                print(f"📁 找到 {len(self.sample_data_files)} 个示例数据文件")
    
    def create_pynsist_cfg(self, temp_dir):
        """创建 pynsist 配置文件"""
        cfg_content = f'''[Application]
name={self.display_name}
version={self.version}
entry_point=源代码.qt_app_v2_optimized_final:main
icon=资源文件/spic_icon.ico

[Python]
version=3.8.10

[Include]
# 本地文件
pypi_wheels = PySide6==6.5.0.1
packages = PySide6
files = 源代码/
        资源文件/
        文档/
        示例数据/
        快速启动.bat
        安装指南.md

# 要排除的包
exclude_packages = test
'''
        
        cfg_file = temp_dir / "installer.cfg"
        with open(cfg_file, 'w', encoding='utf-8') as f:
            f.write(cfg_content)
        
        print(f"✅ 创建 pynsist 配置文件: {cfg_file}")
        return cfg_file
    
    def create_installation_guide(self, temp_dir):
        """创建安装指南"""
        guide_content = f"""# E文件解析工具 安装指南

## 版本信息
- 版本: {self.version}
- 发布时间: {datetime.now().strftime('%Y-%m-%d')}
- 制造商: {self.manufacturer}

## 安装步骤

### 1. 运行安装程序
双击安装包文件开始安装。

### 2. 选择安装位置
安装程序会提示您选择安装目录，默认安装到 Program Files 文件夹。

### 3. 完成安装
安装完成后，您可以在以下位置找到应用程序：
- 开始菜单: {self.app_name}
- 桌面: E文件解析工具 快捷方式（可选）
- 安装目录: 源代码\\qt_app_v2_optimized_final.py

## 使用方法

### 1. 运行应用程序
安装完成后，应用程序会自动包含所需的 Python 环境和依赖。

### 2. 快速启动
双击桌面上的快捷方式或使用开始菜单中的"快速启动"选项。

## 卸载方法

### 方法一：通过控制面板
1. 打开控制面板
2. 选择"程序和功能"
3. 找到"{self.display_name}"
4. 点击"卸载"

### 方法二：通过开始菜单
在开始菜单的程序列表中找到"{self.app_name}"，选择卸载选项。

## 包含文件

### 源代码
- qt_app_v2_optimized_final.py - 主应用程序
- efile_parser_optimized.py - E文件解析器
- db_utils_optimized.py - 数据库工具
- requirements_optimized.txt - 依赖列表
- build_qt_app_v2_optimized.py - 构建脚本

### 资源文件
- spic_icon.ico - 应用图标
- spic_logo.png - SPIC Logo

### 文档
- README.md - 项目说明
- 南方电网新能源数据上送规范 V3.3修订版（2022.2月）.pdf - 规范文档

### 示例数据
包含用于测试的示例 E文件

## 系统要求

- Windows 7 SP1 或更高版本
- 500 MB 可用磁盘空间
- 2 GB RAM（推荐）

## 技术支持

如有问题，请联系：
- 开发者: 陈丰
- 电话: 0871-65666603
- 单位: 国家电投云南国际 昆明生产运营中心

## 版权信息
© {datetime.now().year} {self.manufacturer} 版权所有
"""
        
        guide_file = temp_dir / "安装指南.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        print(f"✅ 创建安装指南: {guide_file}")
        return guide_file
    
    def create_quick_start_script(self, temp_dir):
        """创建快速启动脚本"""
        script_content = '''@echo off
echo.
echo ================================
echo   E文件解析工具 快速启动
echo ================================
echo.
echo 1. 运行源代码版本
echo 2. 构建可执行文件
echo 3. 查看安装指南
echo 4. 退出
echo.
set /p choice=请选择操作 (1-4): 

if "%choice%"=="1" goto run_source
if "%choice%"=="2" goto build_exe
if "%choice%"=="3" goto view_guide
if "%choice%"=="4" goto exit_script

:run_source
echo.
echo 正在启动源代码版本...
cd "源代码"
python qt_app_v2_optimized_final.py
goto end

:build_exe
echo.
echo 正在构建可执行文件...
cd "源代码"
python build_qt_app_v2_optimized.py
echo.
echo 构建完成！可执行文件在 dist 目录中。
pause
goto end

:view_guide
echo.
echo 正在打开安装指南...
start "" "安装指南.md"
goto end

:exit_script
echo.
echo 感谢使用！
goto end

:end
echo.
pause
'''
        
        script_file = temp_dir / "快速启动.bat"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"✅ 创建快速启动脚本: {script_file}")
        return script_file
    
    def copy_files_to_temp(self, temp_dir):
        """复制文件到临时目录"""
        print("📁 复制文件到临时目录...")
        
        # 创建目录结构
        source_dir = temp_dir / "源代码"
        resource_dir = temp_dir / "资源文件"
        doc_dir = temp_dir / "文档"
        sample_dir = temp_dir / "示例数据"
        
        source_dir.mkdir(exist_ok=True)
        resource_dir.mkdir(exist_ok=True)
        doc_dir.mkdir(exist_ok=True)
        sample_dir.mkdir(exist_ok=True)
        
        # 复制文件
        for file_name, category in self.files_to_include:
            src_file = self.project_root / file_name
            if src_file.exists():
                if category == "源代码":
                    dst_file = source_dir / file_name
                elif category == "资源文件":
                    dst_file = resource_dir / file_name
                elif category == "文档":
                    dst_file = doc_dir / file_name
                
                shutil.copy2(src_file, dst_file)
                print(f"  ✅ 复制: {file_name}")
        
        # 复制示例数据
        for sample_file in self.sample_data_files:
            dst_file = sample_dir / sample_file.name
            shutil.copy2(sample_file, dst_file)
            print(f"  ✅ 复制示例数据: {sample_file.name}")
        
        # 创建安装指南和快速启动脚本
        self.create_installation_guide(temp_dir)
        self.create_quick_start_script(temp_dir)
    
    def build_installer(self, temp_dir):
        """构建安装程序"""
        if not self.pynsist_available:
            print("❌ 无法构建安装程序：未找到 pynsist")
            return False
        
        print("🔨 开始构建 PyNSIS 安装程序...")
        
        # 创建配置文件
        cfg_file = self.create_pynsist_cfg(temp_dir)
        
        # 运行 pynsist
        installer_file = self.project_root / f"{self.app_name}_v{self.version}_PyNSIS_安装程序.exe"
        
        pynsist_cmd = [
            sys.executable, "-m", "pynsist",
            str(cfg_file)
        ]
        
        print(f"🔨 运行 pynsist 构建...")
        try:
            result = subprocess.run(pynsist_cmd, cwd=temp_dir, check=True,
                                  capture_output=True, text=True)
            print("  ✅ 构建成功")
            
            # 查找生成的安装程序
            build_dir = temp_dir / "build"
            if build_dir.exists():
                installer_files = list(build_dir.glob("*.exe"))
                if installer_files:
                    # 复制安装程序到项目目录
                    shutil.copy2(installer_files[0], installer_file)
                    print(f"  ✅ 复制安装程序: {installer_file.name}")
                    return installer_file
            
            print("  ❌ 未找到生成的安装程序文件")
            return False
                
        except subprocess.CalledProcessError as e:
            print(f"  ❌ 构建失败: {e}")
            print(f"  错误输出: {e.stderr}")
            return False
    
    def build_installer_simple(self):
        """创建简单的批处理安装脚本（备用方案）"""
        print("🔨 创建简单的批处理安装脚本...")
        
        install_script = self.project_root / "安装程序.bat"
        
        script_content = f'''@echo off
echo.
echo ================================
echo   {self.display_name} 安装程序
echo ================================
echo.
echo 版本: {self.version}
echo 制造商: {self.manufacturer}
echo.
echo 此安装程序将把文件复制到 Program Files 目录。
echo.
pause

echo.
echo 正在创建安装目录...
set "INSTALL_DIR=%ProgramFiles%\\{self.app_name}"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo 正在复制文件...
xcopy /E /I /Y "源代码" "%INSTALL_DIR%\\源代码"
xcopy /E /I /Y "资源文件" "%INSTALL_DIR%\\资源文件"
xcopy /E /I /Y "文档" "%INSTALL_DIR%\\文档"
xcopy /E /I /Y "示例数据" "%INSTALL_DIR%\\示例数据"
copy /Y "快速启动.bat" "%INSTALL_DIR%"
copy /Y "安装指南.md" "%INSTALL_DIR%"

echo.
echo 创建快捷方式...
set "SHORTCUT_DIR=%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\{self.app_name}"
if not exist "%SHORTCUT_DIR%" mkdir "%SHORTCUT_DIR%"

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%SHORTCUT_DIR%\\{self.app_name}.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\\源代码\\qt_app_v2_optimized_final.py" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%\\源代码" >> CreateShortcut.vbs
echo oLink.IconLocation = "%INSTALL_DIR%\\资源文件\\spic_icon.ico" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut2.vbs
echo sLinkFile = "%SHORTCUT_DIR%\\快速启动.lnk" >> CreateShortcut2.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut2.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\\快速启动.bat" >> CreateShortcut2.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut2.vbs
echo oLink.Save >> CreateShortcut2.vbs
cscript CreateShortcut2.vbs
del CreateShortcut2.vbs

echo.
echo 创建桌面快捷方式...
set "DESKTOP_DIR=%USERPROFILE%\\Desktop"
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateDesktopShortcut.vbs
echo sLinkFile = "%DESKTOP_DIR%\\{self.app_name}.lnk" >> CreateDesktopShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateDesktopShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\\源代码\\qt_app_v2_optimized_final.py" >> CreateDesktopShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%\\源代码" >> CreateDesktopShortcut.vbs
echo oLink.IconLocation = "%INSTALL_DIR%\\资源文件\\spic_icon.ico" >> CreateDesktopShortcut.vbs
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
echo    cd "%INSTALL_DIR%\\源代码"
echo    pip install -r requirements_optimized.txt
echo.
echo 请按任意键退出...
pause >nul
'''
        
        with open(install_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"✅ 创建简单安装脚本: {install_script}")
        return install_script
    
    def build_installer(self):
        """构建安装程序"""
        print("=" * 60)
        print("🚀 开始构建 Windows 安装程序")
        print("=" * 60)
        print(f"📦 应用名称: {self.display_name}")
        print(f"📦 版本: {self.version}")
        print(f"📦 制造商: {self.manufacturer}")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # 检查 pynsist
        if self.pynsist_available:
            print("✅ 使用 pynsist 构建专业安装程序")
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                try:
                    # 复制文件
                    self.copy_files_to_temp(temp_path)
                    
                    # 构建安装程序
                    installer_file = self.build_installer(temp_path)
                    
                    if installer_file and installer_file.exists():
                        # 显示构建信息
                        self.show_build_summary(installer_file)
                        print("✅ pynsist 安装程序构建成功！")
                        return True
                    else:
                        print("❌ pynsist 文件生成失败")
                        return False
                    
                except Exception as e:
                    print(f"❌ 构建过程中发生错误: {e}")
                    return False
        else:
            print("⚠️ 未找到 pynsist，使用简单批处理安装脚本")
            installer_file = self.build_installer_simple()
            if installer_file:
                self.show_simple_build_summary(installer_file)
                print("✅ 简单安装脚本创建成功！")
                return True
            return False
    
    def show_build_summary(self, installer_file):
        """显示构建摘要（pynsist）"""
        print("\n" + "=" * 60)
        print("📊 构建摘要 (pynsist)")
        print("=" * 60)
        
        # 文件大小
        file_size = installer_file.stat().st_size / (1024 * 1024)
        print(f"📦 安装程序: {installer_file.name}")
        print(f"📏 文件大小: {file_size:.2f} MB")
        print(f"📁 完整路径: {installer_file}")
        
        print(f"⏰ 构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print("\n🎉 安装程序已准备就绪！")
        print(f"您可以双击 {installer_file.name} 文件来安装应用程序。")
        print("\n💡 pynsist 安装程序特点:")
        print("- 自动包含 Python 运行时")
        print("- 自动安装所有依赖")
        print("- 创建专业的 Windows 安装体验")
    
    def show_simple_build_summary(self, installer_file):
        """显示构建摘要（简单脚本）"""
        print("\n" + "=" * 60)
        print("📊 构建摘要 (简单安装脚本)")
        print("=" * 60)
        
        # 文件大小
        file_size = installer_file.stat().st_size / 1024
        print(f"📦 安装脚本: {installer_file.name}")
        print(f"📏 文件大小: {file_size:.1f} KB")
        print(f"📁 完整路径: {installer_file}")
        
        print(f"⏰ 构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print("\n🎉 安装脚本已准备就绪！")
        print(f"您可以双击 {installer_file.name} 文件来安装应用程序。")
        print("\n⚠️ 注意：这是简单的批处理安装脚本，")
        print("建议安装 pynsist 后重新构建专业安装程序。")


def main():
    """主函数"""
    print("🔧 Windows 安装程序构建工具")
    print("支持 pynsist 和简单批处理安装脚本")
    print("-" * 60)
    
    # 检查 Python 版本
    if sys.version_info < (3, 6):
        print("❌ 错误: 需要 Python 3.6 或更高版本")
        return 1
    
    # 创建构建器并构建安装程序
    builder = PyNSISBuilder()
    success = builder.build_installer()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())