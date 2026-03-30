#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最终构建脚本 - 南网E文件解析工具
国家电投昆明生产运营中心 版权所有
作者: 陈丰 联系电话: 0871-65666603
"""

import os
import sys
import shutil
import subprocess

def main():
    print("🚀 开始构建南网E文件解析工具")
    print("国家电投昆明生产运营中心 版权所有")
    print("版本: 2.2.0")
    print("=" * 50)

    # 清理旧构建
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🗑️ 已删除旧构建目录")
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("🗑️ 已删除旧分发目录")

    # 确保 resources 目录存在并复制资源
    os.makedirs('resources', exist_ok=True)

    # 复制 logo 文件
    if os.path.exists('spic_logo.png'):
        shutil.copy2('spic_logo.png', 'resources/spic_logo.png')
        print("📋 已复制 spic_logo.png")

    # 复制空数据库
    if os.path.exists('eparser_empty.db'):
        shutil.copy2('eparser_empty.db', 'resources/eparser_empty.db')
        print("📋 已复制 eparser_empty.db")

    print("✅ 资源准备完成")

    # 创建 PyInstaller spec 文件
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['qt_app_v2_optimized.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('resources/spic_logo.png', 'resources'),
        ('resources/eparser_empty.db', 'resources'),
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

    # 运行 PyInstaller
    print("🏗️ 正在构建可执行文件...")
    result = subprocess.run(
        'pyinstaller qt_app_v2_optimized.spec --clean',
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ PyInstaller 构建成功!")

        # 创建独立安装包
        if os.path.exists('dist/EFileParser'):
            package_dir = 'EFileParser_Package'
            if os.path.exists(package_dir):
                shutil.rmtree(package_dir)

            shutil.copytree('dist/EFileParser', f'{package_dir}/EFileParser')
            print(f"📦 已创建独立安装包: {package_dir}")

            # 创建 README 文件
            readme_content = '''南网E文件解析工具 v2.2.0
国家电投昆明生产运营中心 版权所有

安装说明:
1. 解压缩此包到任意目录
2. 运行 EFileParser/EFileParser.exe
3. 使用说明请参考内置帮助

联系方式:
- 作者: 陈丰
- 电话: 0871-65666603

版权所有 © 2026 国家电投昆明生产运营中心
'''

            with open(f'{package_dir}/README.txt', 'w', encoding='utf-8') as f:
                f.write(readme_content)

            print("✅ 安装包准备完成!")
            print(f"📁 安装包位置: {os.path.abspath(package_dir)}")
            print(f"🖥️ 可执行文件: {os.path.abspath('dist/EFileParser/EFileParser.exe')}")

            print("\n📝 下一步:")
            print("   1. 可以直接使用 EFileParser_Package 目录作为独立安装包")
            print("   2. 要创建 MSI 安装程序，请安装 WiX Toolset 并运行 build_installer.py")
            print("   3. WiX Toolset 下载: https://wixtoolset.org/")
        else:
            print("❌ 可执行文件未找到")
            return False
    else:
        print(f"❌ 构建失败: {result.stderr}")
        return False

    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 构建完成!")
    else:
        print("\n❌ 构建失败!")
    sys.exit(0 if success else 1)
</write_to_file>