#!/usr/bin/env python3
"""
E文件解析工具打包脚本
将Python应用打包成Windows可执行文件
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查必要的依赖"""
    try:
        import PySide6
        print("✓ PySide6 已安装")
    except ImportError:
        print("✗ PySide6 未安装，请先安装: pip install PySide6")
        return False
    
    try:
        import sqlite3
        print("✓ SQLite3 已安装")
    except ImportError:
        print("✗ SQLite3 未安装")
        return False
    
    return True

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['qt_app_v2_optimized.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('eparser.db', '.'),
        ('eparser.json', '.'),
        ('spic-logo.ico', '.'),
        ('resources/', 'resources/'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='E文件解析工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='spic-logo.ico'
)
'''
    
    with open('qt_app_v2_optimized.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ 创建 spec 文件: qt_app_v2_optimized.spec")

def create_database():
    """创建数据库文件"""
    import sqlite3
    
    # 创建数据库
    conn = sqlite3.connect('eparser.db')
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            file_hash TEXT,
            parse_status TEXT DEFAULT 'pending',
            parse_time DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parse_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER,
            data_type TEXT,
            data_content TEXT,
            parse_error TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES file_records (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ 创建数据库文件: eparser.db")

def create_config():
    """创建配置文件"""
    config = {
        "version": "2.0.0",
        "database_path": "eparser.db",
        "log_level": "INFO",
        "max_file_size": 10485760,
        "supported_extensions": [".dat"],
        "output_format": "json",
        "auto_backup": True,
        "backup_interval": 3600
    }
    
    import json
    with open('eparser.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("✓ 创建配置文件: eparser.json")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 使用PyInstaller构建
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=E文件解析工具',
        '--windowed',
        '--icon=spic-logo.ico',
        '--add-data=eparser.db;.',
        '--add-data=eparser.json;.',
        '--add-data=spic-logo.ico;.',
        '--add-data=resources;resources',
        'qt_app_v2_optimized.py'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ 构建成功!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("✗ 构建失败:")
        print(e.stderr)
        return False

def main():
    """主函数"""
    print("E文件解析工具打包程序")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 创建必要的文件
    print("\n创建必要文件...")
    create_database()
    create_config()
    
    # 创建spec文件
    create_spec_file()
    
    # 构建可执行文件
    if build_executable():
        print("\n" + "=" * 50)
        print("打包完成!")
        print("可执行文件位置: dist/E文件解析工具.exe")
        print("数据库文件: eparser.db")
        print("配置文件: eparser.json")
        print("资源文件: resources/")
    else:
        print("\n" + "=" * 50)
        print("打包失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()