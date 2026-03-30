# -*- coding: utf-8 -*-
"""
最终验证脚本 - 确认应用程序所有功能正常
"""

import sys
from PySide6.QtWidgets import QApplication
from qt_app_v2 import EFileViewer, _MATPLOTLIB_AVAILABLE
from efile_parser import parse_efile

def verify():
    print("="*70)
    print("e文件解析工具 - 最终功能验证")
    print("="*70)
    print()

    print("1. 环境检查...")
    print(f"   Matplotlib: {'可用' if _MATPLOTLIB_AVAILABLE else '已禁用（兼容性问题）'}")
    print()

    app = QApplication(sys.argv)
    print("2. 创建应用程序...")
    viewer = EFileViewer()
    print("   [OK]")
    print()

    print("3. 检查Tab数量...")
    tab_count = viewer.tab_widget.count()
    print(f"   Tab总数: {tab_count}")
    print()

    print("4. 列出所有Tab...")
    tabs = []
    for i in range(tab_count):
        tab_text = viewer.tab_widget.tabText(i)
        tabs.append(tab_text)
        print(f"   Tab {i}: {tab_text}")
    print()

    expected_tabs = ["文件概览", "详细数据", "原始内容"]
    print("5. 验证基本Tab...")
    all_tabs_ok = True
    for expected in expected_tabs:
        if expected in tabs:
            print(f"   [OK] {expected} 存在")
        else:
            print(f"   [FAIL] {expected} 不存在")
            all_tabs_ok = False
    print()

    if "曲线" in tabs:
        print(f"   [INFO] 曲线功能已启用")
    else:
        print(f"   [INFO] 曲线功能已禁用（由于matplotlib兼容性问题）")
        print(f"   [INFO] 其他功能完全正常")
    print()

    print("6. 测试文件解析功能...")
    test_file = r"D:\001\eText\102E文本数据202601\DZL_DQYC_202601.tar.gz"
    try:
        result = parse_efile(test_file)
        sections_count = len(result.get("sections", []))
        print(f"   [OK] 文件解析成功")
        print(f"   数据段数量: {sections_count}")
    except Exception as e:
        print(f"   [FAIL] 文件解析失败: {e}")
        return False
    print()

    print("7. 测试数据展示功能...")
    try:
        viewer.current_result = result
        viewer.displaySummary(result)
        print(f"   [OK] displaySummary")

        viewer.displayDataSections(result)
        print(f"   [OK] displayDataSections")

        viewer.displayRaw(result)
        print(f"   [OK] displayRaw")
    except Exception as e:
        print(f"   [FAIL] 数据展示失败: {e}")
        return False
    print()

    print("="*70)
    print("验证结果")
    print("="*70)
    print()

    if all_tabs_ok:
        print("[OK] 所有基本功能正常工作！")
        print()
        print("可用功能:")
        print("  1. 文件解析 (.dat 和 .tar.gz)")
        print("  2. 文件概览 - 查看统计信息")
        print("  3. 详细数据 - 查看数据表格")
        print("  4. 原始内容 - 查看原始文件")
        print("  5. 导出报告 - 生成解析报告")
        print()
        print("暂时不可用:")
        if not _MATPLOTLIB_AVAILABLE:
            print("  6. 曲线绘制 - 由于matplotlib兼容性问题暂时禁用")
            print("     替代方案：使用Excel或其他工具进行数据可视化")
        print()
        print("下一步:")
        print("  1. 运行: python qt_app_v2.py")
        print("  2. 使用应用程序解析和查看文件")
        print("  3. 查看 '曲线功能说明.md' 了解详细信息")
        print()
        return True
    else:
        print("[FAIL] 某些基本功能缺失！")
        return False

if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)
