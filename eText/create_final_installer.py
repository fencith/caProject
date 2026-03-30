#!/usr/bin/env python3
"""
最终安装包构建器
Final Installer Builder
尝试多种安装包构建方法，选择最佳方案
"""

import os
import sys
import shutil
import subprocess
import tempfile
import importlib.util
from pathlib import Path
from datetime import datetime


class FinalInstallerBuilder:
    """最终安装包构建器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.app_name = "E文件解析工具"
        self.display_name = "E文件解析工具 (优化版)"
        self.version = "2.1.3"
        self.manufacturer = "国家电投云南国际"
        
        # 检测可用的构建工具
        self.available_builders = self.detect_builders()
        
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
    
    def detect_builders(self):
        """检测可用的构建工具"""
        builders = {}
        
        # 检查 pynsist
        try:
            import pynsist
            builders['pynsist'] = {
                'name': 'pynsist',
                'version': pynsist.__version__,
                'available': True,
                'description': 'Python 应用安装包构建器（推荐）'
            }
            print(f"✅ 找到 pynsist: {pynsist.__version__}")
        except ImportError:
            builders['pynsist'] = {
                'name': 'pynsist',
                'available': False,
                'description': 'Python 应用安装包构建器（需要安装: pip install pynsist）'
            }
            print("❌ 未找到 pynsist")
        
        # 检查 Inno Setup
        innosetup_path = self.find_innosetup()
        if innosetup_path:
            builders['innosetup'] = {
                'name': 'innosetup',
                'path': innosetup_path,
                'available': True,
                'description': 'Inno Setup 安装包构建器'
            }
            print(f"✅ 找到 Inno Setup: {innosetup_path}")
        else:
            builders['innosetup'] = {
                'name': 'innosetup',
                'available': False,
                'description': 'Inno Setup 安装包构建器（需要安装 Inno Setup）'
            }
            print("❌ 未找到 Inno Setup")
        
        # 检查 WiX Toolset
        wix_path = self.find_wix_toolset()
        if wix_path:
            builders['wix'] = {
                'name': 'wix',
                'path': wix_path,
                'available': True,
                'description': 'WiX Toolset MSI 安装包构建器'
            }
            print(f"✅ 找到 WiX Toolset: {wix_path}")
        else:
            builders['wix'] = {
                'name': 'wix',
                'available': False,
                'description': 'WiX Toolset MSI 安装包构建器（需要安装 WiX Toolset）'
            }
            print("❌ 未找到 WiX Toolset")
        
        return builders
    
    def find_innosetup(self):
        """查找 Inno Setup 安装路径"""
        possible_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
            r"C:\Program Files\Inno Setup 5\ISCC.exe",
        ]
        
        for path in possible_paths:
            iscc_exe = Path(path)
            if iscc_exe.exists():
                return iscc_exe
        return None
    
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
                return Path(path)
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
    
    def build_with_pynsist(self):
        """使用 pynsist 构建安装包"""
        print("🔨 使用 pynsist 构建安装包...")
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # 复制文件
                self.copy_files_to_temp(temp_path)
                
                # 创建 pynsist 配置文件
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
                
                cfg_file = temp_path / "installer.cfg"
                with open(cfg_file, 'w', encoding='utf-8') as f:
                    f.write(cfg_content)
                
                # 运行 pynsist
                installer_file = self.project_root / f"{self.app_name}_v{self.version}_pynsist_安装程序.exe"
                
                pynsist_cmd = [
                    sys.executable, "-m", "pynsist",
                    str(cfg_file)
                ]
                
                print(f"🔨 运行 pynsist 构建...")
                result = subprocess.run(pynsist_cmd, cwd=temp_path, check=True,
                                      capture_output=True, text=True)
                
                # 查找生成的安装程序
                build_dir = temp_path / "build"
                if build_dir.exists():
                    installer_files = list(build_dir.glob("*.exe"))
                    if installer_files:
                        shutil.copy2(installer_files[0], installer_file)
                        print(f"  ✅ pynsist 构建成功: {installer_file.name}")
                        return installer_file
                
                print("  ❌ pynsist 构建失败：未找到安装程序文件")
                return None
                
            except subprocess.CalledProcessError as e:
                print(f"  ❌ pynsist 构建失败: {e}")
                print(f"  错误输出: {e.stderr}")
                return None
            except Exception as e:
                print(f"  ❌ pynsist 构建过程中发生错误: {e}")
                return None
    
    def build_with_innosetup(self):
        """使用 Inno Setup 构建安装包"""
        print("🔨 使用 Inno Setup 构建安装包...")
        
        innosetup_path = self.available_builders['innosetup']['path']
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # 复制文件
                self.copy_files_to_temp(temp_path)
                
                # 创建 ISS 脚本文件
                iss_content = f'''; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "{self.display_name}"
#define MyAppVersion "{self.version}"
#define MyAppPublisher "{self.manufacturer}"
#define MyAppURL "https://www.spic.com.cn/"
#define MyAppExeName "qt_app_v2_optimized_final.py"
#define MyAppSetupExeName "E文件解析工具_安装程序.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{E9B8F3C2-4D5A-4F1B-8C2E-9F7A6B5D3C1E}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
;AppVerName={{#MyAppName}} {{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DisableDirPage=no
DisableProgramGroupPage=yes
OutputBaseFilename={{#MyAppSetupExeName}}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标"; Flags: unchecked

[Files]
; 源代码文件
Source: "源代码\\qt_app_v2_optimized_final.py"; DestDir: "{{app}}\\源代码"; Flags: ignoreversion
Source: "源代码\\efile_parser_optimized.py"; DestDir: "{{app}}\\源代码"; Flags: ignoreversion
Source: "源代码\\db_utils_optimized.py"; DestDir: "{{app}}\\源代码"; Flags: ignoreversion
Source: "源代码\\requirements_optimized.txt"; DestDir: "{{app}}\\源代码"; Flags: ignoreversion
Source: "源代码\\build_qt_app_v2_optimized.py"; DestDir: "{{app}}\\源代码"; Flags: ignoreversion

; 资源文件
Source: "资源文件\\spic_icon.ico"; DestDir: "{{app}}\\资源文件"; Flags: ignoreversion
Source: "资源文件\\spic_logo.png"; DestDir: "{{app}}\\资源文件"; Flags: ignoreversion

; 文档文件
Source: "文档\\README.md"; DestDir: "{{app}}\\文档"; Flags: ignoreversion
Source: "文档\\南方电网新能源数据上送规范 V3.3修订版（2022.2月）.pdf"; DestDir: "{{app}}\\文档"; Flags: ignoreversion

; 快速启动脚本
Source: "快速启动.bat"; DestDir: "{{app}}"; Flags: ignoreversion

; 安装指南
Source: "安装指南.md"; DestDir: "{{app}}"; Flags: ignoreversion

; 示例数据文件
'''
                
                # 添加示例数据文件
                for sample_file in self.sample_data_files:
                    file_name = sample_file.name
                    iss_content += f'Source: "示例数据\\{file_name}"; DestDir: "{{app}}\\示例数据"; Flags: ignoreversion\n'
                
                iss_content += '''
[Icons]
Name: "{{autoprograms}}\\{{#MyAppName}}"; Filename: "{{app}}\\源代码\\{{#MyAppExeName}}"; WorkingDir: "{{app}}\\源代码"; IconFilename: "{{app}}\\资源文件\\spic_icon.ico"
Name: "{{autoprograms}}\\快速启动"; Filename: "{{app}}\\快速启动.bat"; WorkingDir: "{{app}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\源代码\\{{#MyAppExeName}}"; WorkingDir: "{{app}}\\源代码"; IconFilename: "{{app}}\\资源文件\\spic_icon.ico"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\快速启动.bat"; Description: "{{cm:LaunchProgram,{{#MyAppName}}}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  
  if not RegKeyExists(HKLM, 'SOFTWARE\\Python\\PythonCore') then
  begin
    MsgBox('此应用程序需要 Python 3.8 或更高版本。' + #13#10 +
           '请先安装 Python，然后重新运行安装程序。', mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('安装完成！' + #13#10#13#10 +
           '请按照以下步骤使用应用程序：' + #13#10 +
           '1. 双击桌面上的快捷方式或开始菜单中的程序' + #13#10 +
           '2. 首次运行前请安装 Python 依赖：' + #13#10 +
           '   pip install -r requirements_optimized.txt' + #13#10 +
           '3. 然后运行 qt_app_v2_optimized_final.py', mbInformation, MB_OK);
  end;
end;
'''
                
                iss_file = temp_path / "setup.iss"
                with open(iss_file, 'w', encoding='utf-8') as f:
                    f.write(iss_content)
                
                # 运行 Inno Setup 编译器
                installer_file = self.project_root / f"{self.app_name}_v{self.version}_innosetup_安装程序.exe"
                
                iscc_cmd = [
                    str(innosetup_path),
                    "/Qp",  # 静默编译
                    "/O" + str(self.project_root),
                    str(iss_file)
                ]
                
                print(f"🔨 编译 Inno Setup 脚本...")
                result = subprocess.run(iscc_cmd, cwd=temp_path, check=True,
                                      capture_output=True, text=True)
                
                # 检查输出文件
                expected_output = self.project_root / "E文件解析工具_安装程序.exe"
                if expected_output.exists():
                    shutil.move(str(expected_output), str(installer_file))
                    print(f"  ✅ Inno Setup 构建成功: {installer_file.name}")
                    return installer_file
                
                print("  ❌ Inno Setup 构建失败：未找到安装程序文件")
                return None
                
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Inno Setup 构建失败: {e}")
                print(f"  错误输出: {e.stderr}")
                return None
            except Exception as e:
                print(f"  ❌ Inno Setup 构建过程中发生错误: {e}")
                return None
    
    def build_with_wix(self):
        """使用 WiX Toolset 构建 MSI 安装包"""
        print("🔨 使用 WiX Toolset 构建 MSI 安装包...")
        
        wix_path = self.available_builders['wix']['path']
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # 复制文件
                self.copy_files_to_temp(temp_path)
                
                # 创建 WiX 源文件
                wxs_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
    <Product Id="E9B8F3C2-4D5A-4F1B-8C2E-9F7A6B5D3C1E" 
             Name="{self.display_name}" 
             Language="2052" 
             Version="{self.version}" 
             Manufacturer="{self.manufacturer}" 
             UpgradeCode="A1B2C3D4-E5F6-7890-ABCD-EF1234567890">
        
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
                
                wxs_file = temp_path / "product.wxs"
                with open(wxs_file, 'w', encoding='utf-8') as f:
                    f.write(wxs_content)
                
                # 编译 .wxs 文件为 .wixobj
                candle_exe = wix_path / "candle.exe"
                wixobj_file = temp_path / "product.wixobj"
                
                candle_cmd = [
                    str(candle_exe),
                    "-nologo",
                    "-out", str(wixobj_file),
                    str(wxs_file)
                ]
                
                print(f"🔨 编译 WiX 源文件...")
                result = subprocess.run(candle_cmd, cwd=temp_path, check=True,
                                      capture_output=True, text=True)
                
                # 链接 .wixobj 文件为 .msi
                light_exe = wix_path / "light.exe"
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
                result = subprocess.run(light_cmd, cwd=temp_path, check=True,
                                      capture_output=True, text=True)
                
                if msi_file.exists():
                    print(f"  ✅ WiX MSI 构建成功: {msi_file.name}")
                    return msi_file
                
                print("  ❌ WiX MSI 构建失败：未找到 MSI 文件")
                return None
                
            except subprocess.CalledProcessError as e:
                print(f"  ❌ WiX MSI 构建失败: {e}")
                print(f"  错误输出: {e.stderr}")
                return None
            except Exception as e:
                print(f"  ❌ WiX MSI 构建过程中发生错误: {e}")
                return None
    
    def build_simple_installer(self):
        """创建简单的批处理安装脚本"""
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
        
        print(f"✅ 简单安装脚本创建成功: {install_script.name}")
        return install_script
    
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
        
        # 显示可用的构建工具
        print("\n🔧 可用的构建工具:")
        for builder_name, builder_info in self.available_builders.items():
            status = "✅" if builder_info['available'] else "❌"
            print(f"  {status} {builder_info['description']}")
        
        print("\n🔨 开始尝试构建安装程序...")
        
        # 按优先级尝试构建
        builders_order = ['pynsist', 'innosetup', 'wix']
        
        for builder_name in builders_order:
            if self.available_builders[builder_name]['available']:
                print(f"\n🔄 尝试使用 {self.available_builders[builder_name]['name']}...")
                try:
                    if builder_name == 'pynsist':
                        installer_file = self.build_with_pynsist()
                    elif builder_name == 'innosetup':
                        installer_file = self.build_with_innosetup()
                    elif builder_name == 'wix':
                        installer_file = self.build_with_wix()
                    
                    if installer_file and installer_file.exists():
                        print(f"\n🎉 {self.available_builders[builder_name]['name']} 构建成功！")
                        self.show_build_summary(installer_file, builder_name)
                        return True
                    
                except Exception as e:
                    print(f"❌ {self.available_builders[builder_name]['name']} 构建失败: {e}")
        
        # 如果所有专业构建工具都失败，使用简单安装脚本
        print("\n⚠️ 所有专业构建工具都失败，使用简单批处理安装脚本...")
        installer_file = self.build_simple_installer()
        if installer_file:
            print(f"\n🎉 简单安装脚本创建成功！")
            self.show_simple_build_summary(installer_file)
            return True
        
        print("\n❌ 所有构建方法都失败了")
        return False
    
    def show_build_summary(self, installer_file, builder_name):
        """显示构建摘要"""
        print("\n" + "=" * 60)
        print(f"📊 构建摘要 ({builder_name})")
        print("=" * 60)
        
        # 文件大小
        file_size = installer_file.stat().st_size / (1024 * 1024)
        print(f"📦 安装程序: {installer_file.name}")
        print(f"📏 文件大小: {file_size:.2f} MB")
        print(f"📁 完整路径: {installer_file}")
        
        print(f"⏰ 构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print(f"\n🎉 {builder_name} 安装程序已准备就绪！")
        print(f"您可以双击 {installer_file.name} 文件来安装应用程序。")
        
        if builder_name == 'pynsist':
            print("\n💡 pynsist 安装程序特点:")
            print("- 自动包含 Python 运行时")
            print("- 自动安装所有依赖")
            print("- 创建专业的 Windows 安装体验")
        elif builder_name == 'innosetup':
            print("\n💡 Inno Setup 安装程序特点:")
            print("- 专业的 Windows 安装界面")
            print("- 支持自定义安装选项")
            print("- 完整的卸载支持")
        elif builder_name == 'wix':
            print("\n💡 WiX MSI 安装程序特点:")
            print("- 标准的 Windows MSI 格式")
            print("- 企业级部署支持")
            print("- 完整的安装/卸载日志")
    
    def show_simple_build_summary(self, installer_file):
        """显示简单构建摘要"""
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
        print("建议安装专业构建工具后重新构建。")


def main():
    """主函数"""
    print("🔧 最终 Windows 安装程序构建工具")
    print("尝试多种安装包构建方法，选择最佳方案")
    print("-" * 60)
    
    # 检查 Python 版本
    if sys.version_info < (3, 6):
        print("❌ 错误: 需要 Python 3.6 或更高版本")
        return 1
    
    # 创建构建器并构建安装程序
    builder = FinalInstallerBuilder()
    success = builder.build_installer()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())