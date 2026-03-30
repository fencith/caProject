#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单构建脚本 - 南网E文件解析工具
国家电投昆明生产运营中心 版权所有
作者: 陈丰 联系电话: 0871-65666603
"""

import os
import sys
import shutil
import subprocess

def main():
    print("🚀 开始构建南网E文件解析工具")
    print("=" * 50)

    # 清理旧构建
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')

    # 确保 resources 目录存在并复制资源
    os.makedirs('resources', exist_ok=True)
    if os.path.exists('spic_logo.png'):
        shutil.copy2('spic_logo.png', 'resources')
    if os.path.exists('eparser_empty.db'):
        shutil.copy2('eparser_empty.db', 'resources')

    print("✅ 准备工作完成")

    # 创建 PyInstaller spec 文件
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

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

    print("✅ Spec 文件创建完成")

    # 运行 PyInstaller
    print("🏗️ 正在构建可执行文件...")
    result = subprocess.run(
        'pyinstaller qt_app_v2_optimized.spec --clean',
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ 构建成功!")

        # 创建独立安装包
        if os.path.exists('dist/EFileParser'):
            package_dir = 'EFileParser_Package'
            if os.path.exists(package_dir):
                shutil.rmtree(package_dir)
            shutil.copytree('dist/EFileParser', f'{package_dir}/EFileParser')

            with open(f'{package_dir}/README.txt', 'w', encoding='utf-8') as f:
                f.write('''南网E文件解析工具 v2.2.0
国家电投昆明生产运营中心 版权所有

安装说明:
1. 解压缩此包到任意目录
2. 运行 EFileParser/EFileParser.exe
3. 使用说明请参考内置帮助

联系方式:
- 作者: 陈丰
- 电话: 0871-65666603
''')

            print(f"✅ 独立安装包已创建: {os.path.abspath(package_dir)}")
            print(f"📋 可执行文件: {os.path.abspath('dist/EFileParser/EFileParser.exe')}")
        else:
            print("❌ 可执行文件未找到")
    else:
        print(f"❌ 构建失败: {result.stderr}")

if __name__ == "__main__":
    main()
<task_progress>
- [x] Analyze current qt_app_v2.py program
- [x] Optimize and beautify the code
- [ ] Enhance the UI design
- [ ] Test the application
- [ ] Prepare empty database and logo
- [ ] Create Windows MSI installer
</task_progress>
</write_to_file>