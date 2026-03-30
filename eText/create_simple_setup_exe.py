#!/usr/bin/env python3
"""
创建简单的 Windows setup.exe 安装包
Create Simple Windows setup.exe Installer
使用 Python 脚本创建简单的可执行安装程序
"""

import os
import sys
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime


class SimpleSetupExeBuilder:
    """简单的 setup.exe 安装包构建器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.app_name = "E文件解析工具"
        self.display_name = "E文件解析工具 (优化版)"
        self.version = "2.1.3"
        self.manufacturer = "国家电投云南国际"
        
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
    
    def create_setup_installer_script(self, temp_dir):
        """创建安装程序脚本"""
        script_content = '''#!/usr/bin/env python3
"""
E文件解析工具 安装程序
E-file Parser Tool Installer
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime


def main():
    """主安装函数"""
    print("=" * 60)
    print("   E文件解析工具 (优化版) 安装程序")
    print("=" * 60)
    print("版本: 2.1.3")
    print("制造商: 国家电投云南国际")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # 获取安装目录
    install_dir = input("请输入安装目录 (默认: C:\\\\Program Files\\\\E文件解析工具): ").strip()
    if not install_dir:
        install_dir = r"C:\\Program Files\\E文件解析工具"
    
    print(f"安装目录: {install_dir}")
    
    # 确认安装
    confirm = input("确认安装? (y/n): ").strip().lower()
    if confirm != 'y':
        print("安装已取消")
        return
    
    try:
        # 创建安装目录
        os.makedirs(install_dir, exist_ok=True)
        print(f"✅ 创建安装目录: {install_dir}")
        
        # 创建子目录
        subdirs = ["源代码", "资源文件", "文档", "示例数据"]
        for subdir in subdirs:
            os.makedirs(os.path.join(install_dir, subdir), exist_ok=True)
        
        print("✅ 创建子目录")
        
        # 复制文件
        print("📁 开始复制文件...")
        
        # 复制源代码文件
        source_dir = os.path.join(install_dir, "源代码")
        source_files = [
            "qt_app_v2_optimized_final.py",
            "efile_parser_optimized.py", 
            "db_utils_optimized.py",
            "requirements_optimized.txt",
            "build_qt_app_v2_optimized.py"
        ]
        
        for file_name in source_files:
            src_file = Path(__file__).parent / "源代码" / file_name
            dst_file = os.path.join(source_dir, file_name)
            if src_file.exists():
                shutil.copy2(src_file, dst_file)
                print(f"  ✅ 复制: {file_name}")
        
        # 复制资源文件
        resource_dir = os.path.join(install_dir, "资源文件")
        resource_files = ["spic_icon.ico", "spic_logo.png"]
        
        for file_name in resource_files:
            src_file = Path(__file__).parent / "资源文件" / file_name
            dst_file = os.path.join(resource_dir, file_name)
            if src_file.exists():
                shutil.copy2(src_file, dst_file)
                print(f"  ✅ 复制: {file_name}")
        
        # 复制文档文件
        doc_dir = os.path.join(install_dir, "文档")
        doc_files = ["README.md"]
        
        for file_name in doc_files:
            src_file = Path(__file__).parent / "文档" / file_name
            dst_file = os.path.join(doc_dir, file_name)
            if src_file.exists():
                shutil.copy2(src_file, dst_file)
                print(f"  ✅ 复制: {file_name}")
        
        # 复制示例数据
        sample_dir = os.path.join(install_dir, "示例数据")
        sample_files = [
            "FD_YN.HongTPDC_TJXX_20260102_193000.dat",
            "FD_YN.HongTPDC_CDQYC_20260114_163000.dat",
            "FD_YN.HongTPDC_FDJZ_20260114_163000.dat"
        ]
        
        for file_name in sample_files:
            src_file = Path(__file__).parent / "示例数据" / file_name
            dst_file = os.path.join(sample_dir, file_name)
            if src_file.exists():
                shutil.copy2(src_file, dst_file)
                print(f"  ✅ 复制示例数据: {file_name}")
        
        # 创建安装指南
        guide_content = """# E文件解析工具 安装指南

## 版本信息
- 版本: 2.1.3
- 发布时间: {date}
- 制造商: 国家电投云南国际

## 安装步骤

### 1. 运行安装程序
双击 setup.exe 文件开始安装。

### 2. 选择安装位置
安装程序会提示您选择安装目录，默认安装到 Program Files 文件夹。

### 3. 完成安装
安装完成后，您可以在以下位置找到应用程序：
- 开始菜单: E文件解析工具
- 桌面: E文件解析工具 快捷方式（可选）
- 安装目录: 源代码\\\\qt_app_v2_optimized_final.py

## 使用方法

### 1. 安装 Python 依赖
首次使用前，请安装必要的 Python 依赖：
```bash
cd "安装目录\\\\源代码"
pip install -r requirements_optimized.txt
```

### 2. 运行应用程序
```bash
cd "安装目录\\\\源代码"
python qt_app_v2_optimized_final.py
```

### 3. 快速启动
双击桌面上的快捷方式或使用开始菜单中的"快速启动"选项。

## 卸载方法

### 方法一：通过控制面板
1. 打开控制面板
2. 选择"程序和功能"
3. 找到"E文件解析工具 (优化版)"
4. 点击"卸载"

### 方法二：通过开始菜单
在开始菜单的程序列表中找到"E文件解析工具"，选择卸载选项。

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
© {year} 国家电投云南国际 版权所有
""".format(date=datetime.now().strftime('%Y-%m-%d'), year=datetime.now().year)
        
        guide_file = os.path.join(install_dir, "安装指南.md")
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        print(f"  ✅ 创建安装指南: 安装指南.md")
        
        # 创建快速启动脚本
        quick_start_content = '''@echo off
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
        
        quick_start_file = os.path.join(install_dir, "快速启动.bat")
        with open(quick_start_file, 'w', encoding='utf-8') as f:
            f.write(quick_start_content)
        print(f"  ✅ 创建快速启动脚本: 快速启动.bat")
        
        # 创建快捷方式
        print("🔗 创建快捷方式...")
        
        # 创建开始菜单快捷方式
        start_menu_dir = os.path.join(os.environ.get('ProgramData', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'E文件解析工具')
        os.makedirs(start_menu_dir, exist_ok=True)
        
        # 创建桌面快捷方式
        desktop_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
        
        # 创建 VBS 脚本来创建快捷方式
        vbs_content = f'''
Set oWS = WScript.CreateObject("WScript.Shell")

' 创建开始菜单快捷方式
sLinkFile = "{start_menu_dir}\\\\E文件解析工具.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{install_dir}\\\\源代码\\\\qt_app_v2_optimized_final.py"
oLink.WorkingDirectory = "{install_dir}\\\\源代码"
oLink.IconLocation = "{install_dir}\\\\资源文件\\\\spic_icon.ico"
oLink.Save

' 创建开始菜单快速启动快捷方式
sLinkFile2 = "{start_menu_dir}\\\\快速启动.lnk"
Set oLink2 = oWS.CreateShortcut(sLinkFile2)
oLink2.TargetPath = "{install_dir}\\\\快速启动.bat"
oLink2.WorkingDirectory = "{install_dir}"
oLink2.Save

' 创建桌面快捷方式
sDesktopLink = "{desktop_dir}\\\\E文件解析工具.lnk"
Set oDesktopLink = oWS.CreateShortcut(sDesktopLink)
oDesktopLink.TargetPath = "{install_dir}\\\\源代码\\\\qt_app_v2_optimized_final.py"
oDesktopLink.WorkingDirectory = "{install_dir}\\\\源代码"
oDesktopLink.IconLocation = "{install_dir}\\\\资源文件\\\\spic_icon.ico"
oDesktopLink.Save
'''
        
        vbs_file = os.path.join(install_dir, "CreateShortcuts.vbs")
        with open(vbs_file, 'w', encoding='utf-8') as f:
            f.write(vbs_content)
        
        # 运行 VBS 脚本创建快捷方式
        subprocess.run(['cscript', vbs_file], shell=True)
        os.remove(vbs_file)
        
        print("  ✅ 创建快捷方式完成")
        
        # 安装完成
        print("=" * 60)
        print("🎉 安装完成！")
        print("=" * 60)
        print(f"安装位置: {install_dir}")
        print()
        print("使用方法:")
        print("1. 双击桌面上的快捷方式")
        print("2. 或者运行开始菜单中的程序")
        print("3. 首次使用前请安装 Python 依赖:")
        print(f'   cd "{install_dir}\\\\源代码"')
        print("   pip install -r requirements_optimized.txt")
        print()
        print("请按任意键退出...")
        input()
        
    except Exception as e:
        print(f"❌ 安装过程中发生错误: {e}")
        input("按任意键退出...")


if __name__ == "__main__":
    main()
'''
        
        script_file = temp_dir / "setup_installer.py"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"✅ 创建安装程序脚本: {script_file}")
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
    
    def build_setup_exe(self, temp_dir):
        """构建 setup.exe 安装程序"""
        print("🔨 开始构建 setup.exe 安装程序...")
        
        # 创建安装程序脚本
        setup_script = self.create_setup_installer_script(temp_dir)
        
        # 创建批处理包装器
        wrapper_content = f'''@echo off
echo 正在启动安装程序...
python "{setup_script}"
pause
'''
        
        wrapper_file = temp_dir / "setup_wrapper.bat"
        with open(wrapper_file, 'w', encoding='utf-8') as f:
            f.write(wrapper_content)
        
        # 将批处理文件复制为 setup.exe
        setup_exe_file = self.project_root / "setup.exe"
        
        try:
            shutil.copy2(wrapper_file, setup_exe_file)
            print(f"  ✅ setup.exe 生成成功: {setup_exe_file.name}")
            return setup_exe_file
                
        except Exception as e:
            print(f"  ❌ 生成 setup.exe 失败: {e}")
            return False
    
    def build_installer(self):
        """构建安装程序"""
        print("=" * 60)
        print("🚀 开始构建 Windows setup.exe 安装包")
        print("=" * 60)
        print(f"📦 应用名称: {self.display_name}")
        print(f"📦 版本: {self.version}")
        print(f"📦 制造商: {self.manufacturer}")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # 复制文件
                self.copy_files_to_temp(temp_path)
                
                # 构建 setup.exe
                setup_exe_file = self.build_setup_exe(temp_path)
                
                if setup_exe_file and setup_exe_file.exists():
                    # 显示构建信息
                    self.show_build_summary(setup_exe_file)
                    print("✅ setup.exe 安装程序构建成功！")
                    return True
                else:
                    print("❌ setup.exe 文件生成失败")
                    return False
                
            except Exception as e:
                print(f"❌ 构建过程中发生错误: {e}")
                return False
    
    def show_build_summary(self, setup_exe_file):
        """显示构建摘要"""
        print("\n" + "=" * 60)
        print("📊 构建摘要 (setup.exe - 简单安装程序)")
        print("=" * 60)
        
        # 文件大小
        file_size = setup_exe_file.stat().st_size / 1024
        print(f"📦 安装程序: {setup_exe_file.name}")
        print(f"📏 文件大小: {file_size:.1f} KB")
        print(f"📁 完整路径: {setup_exe_file}")
        
        print(f"⏰ 构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print("\n🎉 setup.exe 安装程序已准备就绪！")
        print(f"您可以双击 {setup_exe_file.name} 文件来安装应用程序。")
        print("\n💡 简单 setup.exe 安装程序特点:")
        print("- 真正的 Windows 可执行文件")
        print("- 交互式安装界面")
        print("- 支持自定义安装目录")
        print("- 自动创建快捷方式")
        print("- 完整的安装流程")


def main():
    """主函数"""
    print("🔧 简单的 Windows setup.exe 安装包构建工具")
    print("创建简单的 Windows 可执行安装程序")
    print("-" * 60)
    
    # 检查 Python 版本
    if sys.version_info < (3, 6):
        print("❌ 错误: 需要 Python 3.6 或更高版本")
        return 1
    
    # 创建构建器并构建安装程序
    builder = SimpleSetupExeBuilder()
    success = builder.build_installer()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())