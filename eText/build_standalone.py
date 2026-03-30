#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
E文件解析工具 - 独立可执行文件构建脚本
国家电投昆明生产运营中心 版权所有
作者: 陈丰 联系电话: 0871-65666603
"""

import os
import sys
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

def run_command(cmd, cwd=None, description=""):
    """运行命令并显示输出"""
    print(f"🔧 {description}")
    print(f"📝 命令: {cmd}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=True
        )
        print(f"✅ 成功: {description}")
        if result.stdout:
            print(f"📋 输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 失败: {description}")
        print(f"📋 错误: {e.stderr}")
        return False

def clean_build_directories():
    """清理构建目录"""
    print("🧹 清理构建目录...")

    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️ 已删除 {dir_name}")

    # 创建新的构建目录
    os.makedirs('build', exist_ok=True)
    os.makedirs('dist', exist_ok=True)
    print("✅ 构建目录已准备就绪")

def copy_resources():
    """复制资源文件"""
    print("📁 复制资源文件...")

    # 确保 resources 目录存在
    os.makedirs('resources', exist_ok=True)

    # 复制 logo 文件
    logo_files = ['spic_logo.png', 'spic-logo.svg']
    for logo_file in logo_files:
        if os.path.exists(logo_file):
            shutil.copy2(logo_file, 'resources')
            print(f"📋 已复制 {logo_file} 到 resources")

    # 复制空数据库
    if os.path.exists('eparser_empty.db'):
        shutil.copy2('eparser_empty.db', 'resources')
        print(f"📋 已复制 eparser_empty.db 到 resources")

    # 复制其他资源文件
    resource_files = ['folder.png', 'parse.png', 'database.png', 'export.png',
                     'refresh.png', 'delete.png', 'clear.png']
    for res_file in resource_files:
        if os.path.exists(res_file):
            shutil.copy2(res_file, 'resources')
            print(f"📋 已复制 {res_file} 到 resources")

def create_pyinstaller_spec():
    """创建 PyInstaller spec 文件"""
    print("📄 创建 PyInstaller spec 文件...")

    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['qt_app_v2_optimized.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('resources/spic_logo.png', 'resources'),
        ('resources/spic-logo.svg', 'resources'),
        ('resources/eparser_empty.db', 'resources'),
        ('resources/folder.png', 'resources'),
        ('resources/parse.png', 'resources'),
        ('resources/database.png', 'resources'),
        ('resources/export.png', 'resources'),
        ('resources/refresh.png', 'resources'),
        ('resources/delete.png', 'resources'),
        ('resources/clear.png', 'resources'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EFileParser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='resources/spic_logo.png'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='EFileParser'
)
'''

    with open('qt_app_v2_optimized.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("✅ PyInstaller spec 文件已创建")

def build_with_pyinstaller():
    """使用 PyInstaller 构建可执行文件"""
    print("🏗️ 使用 PyInstaller 构建可执行文件...")

    # 创建 spec 文件
    create_pyinstaller_spec()

    # 构建可执行文件
    success = run_command(
        'pyinstaller qt_app_v2_optimized.spec --clean --noconfirm',
        description="运行 PyInstaller 构建"
    )

    if success:
        print("✅ PyInstaller 构建完成")
        return True
    else:
        print("❌ PyInstaller 构建失败")
        return False

def create_standalone_package():
    """创建独立安装包"""
    print("📦 创建独立安装包...")

    # 创建输出目录
    output_dir = "EFileParser_Package"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    os.makedirs(output_dir, exist_ok=True)

    # 复制可执行文件和资源
    exe_source = "dist/EFileParser"
    if os.path.exists(exe_source):
        shutil.copytree(exe_source, f"{output_dir}/EFileParser")
        print(f"📋 已复制可执行文件到 {output_dir}")

        # 创建 README
        readme_content = f"""南网E文件解析工具 v2.2.0
国家电投昆明生产运营中心 版权所有

安装说明:
1. 解压缩此包到任意目录
2. 运行 EFileParser/EFileParser.exe
3. 使用说明请参考内置帮助

联系方式:
- 作者: 陈丰
- 电话: 0871-65666603

版权所有 © 2026 国家电投昆明生产运营中心
"""

        with open(f"{output_dir}/README.txt", 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print("✅ 独立安装包已创建")

        return True
    else:
        print("❌ 可执行文件不存在")
        return False

def create_batch_scripts():
    """创建批处理脚本"""
    print("📜 创建批处理脚本...")

    # 创建构建脚本
    build_script = '''@echo off
echo 🏗️ 开始构建南网E文件解析工具...
echo.

python build_standalone.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ 构建完成!
    echo.
    echo 独立安装包: EFileParser_Package
    echo 可执行文件: dist/EFileParser/EFileParser.exe
    echo.
    pause
) else (
    echo.
    echo ❌ 构建失败!
    echo.
    pause
)
'''

    with open('build_standalone.bat', 'w', encoding='utf-8') as f:
        f.write(build_script)

    print("✅ 构建脚本已创建: build_standalone.bat")

def main():
    """主函数"""
    print("🚀 开始构建南网E文件解析工具独立版本")
    print("=" * 60)
    print("国家电投昆明生产运营中心 版权所有")
    print("版本: 2.2.0")
    print("=" * 60)
    print()

    # 检查依赖
    print("🔍 检查依赖...")

    dependencies = [
        ('python', 'Python'),
        ('pip', 'pip'),
        ('pyinstaller', 'PyInstaller')
    ]

    missing_deps = []
    for cmd, name in dependencies:
        try:
            result = subprocess.run(f'{cmd} --version', shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                missing_deps.append(name)
        except:
            missing_deps.append(name)

    if missing_deps:
        print(f"❌ 缺少依赖: {', '.join(missing_deps)}")
        print("请安装所有依赖后重试。")
        return False

    print("✅ 所有依赖已安装")

    # 清理构建目录
    clean_build_directories()

    # 复制资源文件
    copy_resources()

    # 构建可执行文件
    if not build_with_pyinstaller():
        print("❌ 构建过程终止")
        return False

    # 创建独立安装包
    if not create_standalone_package():
        print("❌ 独立安装包创建失败")
        return False

    # 创建批处理脚本
    create_batch_scripts()

    print("🎉 构建完成!")
    print(f"📦 独立安装包: {os.path.abspath('EFileParser_Package')}")
    print(f"🖥️ 可执行文件: {os.path.abspath('dist/EFileParser/EFileParser.exe')}")
    print(f"📁 输出目录: {os.path.abspath('dist/EFileParser')}")

    print("\n📝 关于MSI安装程序:")
    print("   由于WiX Toolset未安装，无法创建MSI安装程序。")
    print("   请安装WiX Toolset后使用 build_installer.py 创建MSI。")
    print("   下载地址: https://wixtoolset.org/")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
</write_to_file>