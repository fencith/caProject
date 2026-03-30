# -*- coding: utf-8 -*-
"""
曲线栏目问题诊断和解决方案
"""

import sys
import os

def check_environment():
    """检查环境配置"""
    print("="*60)
    print("环境检查")
    print("="*60)
    print()
    
    # 1. 检查Python版本
    print(f"1. Python版本: {sys.version}")
    print()
    
    # 2. 检查matplotlib
    print(f"2. 检查matplotlib...")
    try:
        import matplotlib
        print(f"   matplotlib版本: {matplotlib.__version__}")
        print(f"   matplotlib可用: 是")
        matplotlib_ok = True
    except ImportError:
        print(f"   matplotlib可用: 否")
        print(f"   解决方案: pip install matplotlib")
        matplotlib_ok = False
    print()
    
    # 3. 检查PySide6
    print(f"3. 检查PySide6...")
    try:
        import PySide6
        print(f"   PySide6版本: {PySide6.__version__}")
        print(f"   PySide6可用: 是")
        pyside6_ok = True
    except ImportError:
        print(f"   PySide6可用: 否")
        print(f"   解决方案: pip install PySide6")
        pyside6_ok = False
    print()
    
    # 4. 检查efile_parser
    print(f"4. 检查efile_parser...")
    try:
        import efile_parser
        print(f"   efile_parser可用: 是")
        efile_ok = True
    except ImportError:
        print(f"   efile_parser可用: 否")
        efile_ok = False
    print()
    
    # 5. 检查qt_app_v2.py文件
    print(f"5. 检查qt_app_v2.py文件...")
    qt_app_path = r"D:\001\eText\qt_app_v2.py"
    if os.path.exists(qt_app_path):
        print(f"   文件存在: 是")
        print(f"   文件路径: {qt_app_path}")
        print(f"   文件大小: {os.path.getsize(qt_app_path)} 字节")
        
        # 读取文件检查关键代码
        with open(qt_app_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查关键代码段
        checks = [
            ("matplotlib导入", "import matplotlib"),
            ("曲线Tab创建", 'self.tab_widget.addTab(self.curve_tab, "曲线")'),
            ("MATPLOTLIB_AVAILABLE检查", "_MATPLOTLIB_AVAILABLE"),
            ("initCurveTab方法", "def initCurveTab(self)"),
        ]
        
        print()
        print(f"   代码检查:")
        all_checks_ok = True
        for name, code in checks:
            found = code in content
            status = "[OK]" if found else "[FAIL]"
            print(f"     {status} {name}")
            if not found:
                all_checks_ok = False
        
        qt_app_ok = all_checks_ok
    else:
        print(f"   文件存在: 否")
        print(f"   错误: qt_app_v2.py文件未找到")
        qt_app_ok = False
    print()
    
    # 总结
    print("="*60)
    print("检查总结")
    print("="*60)
    print()
    print(f"matplotlib: {'[OK]' if matplotlib_ok else '[FAIL]'}")
    print(f"PySide6: {'[OK]' if pyside6_ok else '[FAIL]'}")
    print(f"efile_parser: {'[OK]' if efile_ok else '[FAIL]'}")
    print(f"qt_app_v2.py: {'[OK]' if qt_app_ok else '[FAIL]'}")
    print()

    all_ok = matplotlib_ok and pyside6_ok and efile_ok and qt_app_ok
    if all_ok:
        print("[OK] 所有检查通过！")
        print()
        print("接下来:")
        print("1. 运行: python check_curve_configuration.py")
        print("2. 运行: python qt_app_v2.py")
        print("3. 在应用程序中检查'曲线'栏目（应该是第4个Tab）")
    else:
        print("[FAIL] 检查发现问题！")
        print()
        print("解决方案:")
        if not matplotlib_ok:
            print("  1. 安装matplotlib: pip install matplotlib")
        if not pyside6_ok:
            print("  2. 安装PySide6: pip install PySide6")
        if not efile_ok:
            print("  3. 确保efile_parser.py在当前目录")
        if not qt_app_ok:
            print("  4. 确保qt_app_v2.py文件完整")
    
    print()
    print("="*60)

if __name__ == "__main__":
    check_environment()
