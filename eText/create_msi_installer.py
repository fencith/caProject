#!/usr/bin/env python3
"""
创建 Windows MSI 安装包
Create Windows MSI Installer
使用 WiX Toolset 创建专业的 Windows 安装程序
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET


class MSIInstallerBuilder:
    """MSI 安装包构建器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.app_name = "E文件解析工具"
        self.display_name = "E文件解析工具 (优化版)"
        self.version = "2.1.3"
        self.manufacturer = "国家电投云南国际"
        self.product_code = "E9B8F3C2-4D5A-4F1B-8C2E-9F7A6B5D3C1E"
        self.upgrade_code = "A1B2C3D4-E5F6-7890-ABCD-EF1234567890"
        
        # WiX 工具路径
        self.wix_path = self.find_wix_toolset()
        
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
    
    def find_wix_toolset(self):
        """查找 WiX Toolset 安装路径"""
        possible_paths = [
            r"C:\Program Files (x86)\WiX Toolset v3.11\bin",
            r"C:\Program Files\WiX Toolset v3.11\bin",
            r"C:\Program Files (x86)\WiX Toolset v4.0\bin",
            r"C:\Program Files\WiX Toolset v4.0\bin",
        ]
        
        for path in possible_paths:
            candle_exe = Path(path) / "candle.exe"
            light_exe = Path(path) / "light.exe"
            if candle_exe.exists() and light_exe.exists():
                print(f"✅ 找到 WiX Toolset: {path}")
                return Path(path)
        
        print("❌ 未找到 WiX Toolset，请先安装 WiX Toolset")
        print("下载地址: https://wixtoolset.org/releases/")
        return None
    
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
    
    def create_wxs_file(self, temp_dir):
        """创建 WiX 源文件 (.wxs)"""
        wxs_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
    <Product Id="{self.product_code}" 
             Name="{self.display_name}" 
             Language="2052" 
             Version="{self.version}" 
             Manufacturer="{self.manufacturer}" 
             UpgradeCode="{self.upgrade_code}">
        
        <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" />
        
        <MajorUpgrade DowngradeErrorMessage="新版本已安装，无法降级安装。" />
        
        <MediaTemplate />
        
        <Feature Id="ProductFeature" Title="主程序" Level="1">
            <ComponentGroupRef Id="ProductComponents" />
            <ComponentGroupRef Id="SampleDataComponents" />
        </Feature>
        
        <!-- 安装条件检查 -->
        <Condition Message="此应用程序需要 .NET Framework 4.8 或更高版本。">
            <![CDATA[Installed OR (NETFRAMEWORK48 OR NETFRAMEWORK47 OR NETFRAMEWORK46 OR NETFRAMEWORK45 OR NETFRAMEWORK40)]]>
        </Condition>
        
        <!-- 安装目录选择 -->
        <Directory Id="TARGETDIR" Name="SourceDir">
            <Directory Id="ProgramFilesFolder">
                <Directory Id="INSTALLFOLDER" Name="{self.app_name}">
                    <!-- 源代码目录 -->
                    <Directory Id="SourceDir" Name="源代码" />
                    
                    <!-- 资源文件目录 -->
                    <Directory Id="ResourceDir" Name="资源文件" />
                    
                    <!-- 文档目录 -->
                    <Directory Id="DocDir" Name="文档" />
                    
                    <!-- 示例数据目录 -->
                    <Directory Id="SampleDir" Name="示例数据" />
                </Directory>
            </Directory>
            
            <!-- 开始菜单快捷方式 -->
            <Directory Id="ProgramMenuFolder">
                <Directory Id="ApplicationProgramsFolder" Name="{self.app_name}" />
            </Directory>
            
            <!-- 桌面快捷方式 -->
            <Directory Id="DesktopFolder" Name="Desktop" />
        </Directory>
        
        <!-- 组件定义 -->
        <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
            <!-- 源代码文件 -->
            <Component Id="SourceFiles" Guid="*">
                <File Id="QtApp" Name="qt_app_v2_optimized_final.py" Source="源代码\qt_app_v2_optimized_final.py" KeyPath="yes" />
                <File Id="EFileParser" Name="efile_parser_optimized.py" Source="源代码\efile_parser_optimized.py" />
                <File Id="DbUtils" Name="db_utils_optimized.py" Source="源代码\db_utils_optimized.py" />
                <File Id="Requirements" Name="requirements_optimized.txt" Source="源代码\requirements_optimized.txt" />
                <File Id="BuildScript" Name="build_qt_app_v2_optimized.py" Source="源代码\build_qt_app_v2_optimized.py" />
            </Component>
            
            <!-- 资源文件 -->
            <Component Id="ResourceFiles" Guid="*">
                <File Id="IconFile" Name="spic_icon.ico" Source="资源文件\spic_icon.ico" />
                <File Id="LogoFile" Name="spic_logo.png" Source="资源文件\spic_logo.png" />
            </Component>
            
            <!-- 文档文件 -->
            <Component Id="DocFiles" Guid="*">
                <File Id="ReadmeFile" Name="README.md" Source="文档\README.md" />
                <File Id="SpecFile" Name="南方电网新能源数据上送规范 V3.3修订版（2022.2月）.pdf" Source="文档\南方电网新能源数据上送规范 V3.3修订版（2022.2月）.pdf" />
            </Component>
            
            <!-- 快速启动脚本 -->
            <Component Id="QuickStartScript" Guid="*">
                <File Id="QuickStart" Name="快速启动.bat" Source="快速启动.bat" />
            </Component>
            
            <!-- 安装指南 -->
            <Component Id="InstallGuide" Guid="*">
                <File Id="InstallGuideFile" Name="安装指南.md" Source="安装指南.md" />
            </Component>
        </ComponentGroup>
        
        <!-- 示例数据组件 -->
        <ComponentGroup Id="SampleDataComponents" Directory="SampleDir">
'''
        
        # 添加示例数据文件
        for i, sample_file in enumerate(self.sample_data_files):
            file_id = f"SampleFile{i+1}"
            file_name = sample_file.name
            wxs_content += f'''            <Component Id="{file_id}" Guid="*">
                <File Id="{file_id}File" Name="{file_name}" Source="示例数据\{file_name}" />
            </Component>
'''
        
        wxs_content += '''        </ComponentGroup>
        
        <!-- 快捷方式 -->
        <DirectoryRef Id="ApplicationProgramsFolder">
            <Component Id="ApplicationShortcut" Guid="*">
                <Shortcut Id="ApplicationStartMenuShortcut" 
                          Name="{self.display_name}" 
                          Description="E文件解析工具" 
                          Target="[INSTALLFOLDER]源代码\qt_app_v2_optimized_final.py" 
                          WorkingDirectory="SourceDir">
                    <Icon Id="ApplicationShortcutIcon" SourceFile="资源文件\spic_icon.ico" />
                </Shortcut>
                <Shortcut Id="QuickStartShortcut" 
                          Name="快速启动" 
                          Description="快速启动脚本" 
                          Target="[INSTALLFOLDER]快速启动.bat" 
                          WorkingDirectory="INSTALLFOLDER" />
                <RemoveFolder Id="RemoveProgramMenuDir" Directory="ApplicationProgramsFolder" On="uninstall" />
                <RegistryValue Root="HKCU" Key="Software\{self.manufacturer}\{self.app_name}" Name="installed" Type="integer" Value="1" KeyPath="yes" />
            </Component>
        </DirectoryRef>
        
        <DirectoryRef Id="DesktopFolder">
            <Component Id="DesktopShortcut" Guid="*">
                <Shortcut Id="DesktopShortcut" 
                          Name="{self.app_name}" 
                          Description="E文件解析工具桌面快捷方式" 
                          Target="[INSTALLFOLDER]源代码\qt_app_v2_optimized_final.py" 
                          WorkingDirectory="SourceDir">
                    <Icon Id="DesktopShortcutIcon" SourceFile="资源文件\spic_icon.ico" />
                </Shortcut>
                <RemoveFolder Id="RemoveDesktopDir" Directory="DesktopFolder" On="uninstall" />
                <RegistryValue Root="HKCU" Key="Software\{self.manufacturer}\{self.app_name}" Name="desktopShortcut" Type="integer" Value="1" KeyPath="yes" />
            </Component>
        </DirectoryRef>
        
        <!-- 安装事件 -->
        <InstallExecuteSequence>
            <Custom Action="SetInstallFolder" Before="InstallInitialize">NOT Installed</Custom>
        </InstallExecuteSequence>
        
        <CustomAction Id="SetInstallFolder" Property="INSTALLFOLDER" Value="[ProgramFilesFolder]{self.app_name}" />
    </Product>
</Wix>
'''
        
        wxs_file = temp_dir / "product.wxs"
        with open(wxs_file, 'w', encoding='utf-8') as f:
            f.write(wxs_content)
        
        print(f"✅ 创建 WiX 源文件: {wxs_file}")
        return wxs_file
    
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
- 桌面: E文件解析工具 快捷方式
- 安装目录: 源代码\\qt_app_v2_optimized_final.py

## 使用方法

### 1. 安装 Python 依赖
首次使用前，请安装必要的 Python 依赖：
```bash
cd "安装目录\\源代码"
pip install -r requirements_optimized.txt
```

### 2. 运行应用程序
```bash
cd "安装目录\\源代码"
python qt_app_v2_optimized_final.py
```

### 3. 快速启动
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
- .NET Framework 4.8 或更高版本
- Python 3.8 或更高版本（运行时需要）

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
    
    def build_msi(self, temp_dir):
        """构建 MSI 安装包"""
        if not self.wix_path:
            print("❌ 无法构建 MSI：未找到 WiX Toolset")
            return False
        
        print("🔨 开始构建 MSI 安装包...")
        
        # 创建 WiX 源文件
        wxs_file = self.create_wxs_file(temp_dir)
        
        # 编译 .wxs 文件为 .wixobj
        candle_exe = self.wix_path / "candle.exe"
        wixobj_file = temp_dir / "product.wixobj"
        
        candle_cmd = [
            str(candle_exe),
            "-nologo",
            "-out", str(wixobj_file),
            str(wxs_file)
        ]
        
        print(f"🔨 编译 WiX 源文件...")
        try:
            result = subprocess.run(candle_cmd, cwd=temp_dir, check=True, 
                                  capture_output=True, text=True)
            print("  ✅ 编译成功")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ 编译失败: {e}")
            print(f"  错误输出: {e.stderr}")
            return False
        
        # 链接 .wixobj 文件为 .msi
        light_exe = self.wix_path / "light.exe"
        msi_file = self.project_root / f"{self.app_name}_v{self.version}.msi"
        
        light_cmd = [
            str(light_exe),
            "-nologo",
            "-ext", "WixUIExtension",
            "-ext", "WixUtilExtension",
            "-out", str(msi_file),
            str(wixobj_file)
        ]
        
        print(f"🔨 链接生成 MSI 文件...")
        try:
            result = subprocess.run(light_cmd, cwd=temp_dir, check=True,
                                  capture_output=True, text=True)
            print("  ✅ 链接成功")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ 链接失败: {e}")
            print(f"  错误输出: {e.stderr}")
            return False
        
        return msi_file
    
    def build_installer(self):
        """构建安装程序"""
        print("=" * 60)
        print("🚀 开始构建 Windows MSI 安装包")
        print("=" * 60)
        print(f"📦 应用名称: {self.display_name}")
        print(f"📦 版本: {self.version}")
        print(f"📦 制造商: {self.manufacturer}")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # 检查 WiX Toolset
        if not self.wix_path:
            print("❌ 构建失败：未找到 WiX Toolset")
            print("请先安装 WiX Toolset: https://wixtoolset.org/releases/")
            return False
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # 复制文件
                self.copy_files_to_temp(temp_path)
                
                # 构建 MSI
                msi_file = self.build_msi(temp_path)
                
                if msi_file and msi_file.exists():
                    # 显示构建信息
                    self.show_build_summary(msi_file)
                    print("✅ MSI 安装包构建成功！")
                    return True
                else:
                    print("❌ MSI 文件生成失败")
                    return False
                
            except Exception as e:
                print(f"❌ 构建过程中发生错误: {e}")
                return False
    
    def show_build_summary(self, msi_file):
        """显示构建摘要"""
        print("\n" + "=" * 60)
        print("📊 构建摘要")
        print("=" * 60)
        
        # 文件大小
        file_size = msi_file.stat().st_size / (1024 * 1024)
        print(f"📦 MSI 安装包: {msi_file.name}")
        print(f"📏 文件大小: {file_size:.2f} MB")
        print(f"📁 完整路径: {msi_file}")
        
        print(f"⏰ 构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print("\n🎉 安装包已准备就绪！")
        print(f"您可以双击 {msi_file.name} 文件来安装应用程序。")


def main():
    """主函数"""
    print("🔧 Windows MSI 安装包构建工具")
    print("使用 WiX Toolset 创建专业的 Windows 安装程序")
    print("-" * 60)
    
    # 检查 Python 版本
    if sys.version_info < (3, 6):
        print("❌ 错误: 需要 Python 3.6 或更高版本")
        return 1
    
    # 创建构建器并构建安装包
    builder = MSIInstallerBuilder()
    success = builder.build_installer()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())