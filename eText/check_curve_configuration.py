# -*- coding: utf-8 -*-
"""
检查曲线栏目创建过程中的问题
"""

import sys
from PySide6.QtWidgets import QApplication
from qt_app_v2 import _MATPLOTLIB_AVAILABLE

def main():
    print("="*60)
    print("检查曲线栏目配置")
    print("="*60)
    print()
    
    print(f"1. 检查matplotlib可用性:")
    print(f"   _MATPLOTLIB_AVAILABLE = {_MATPLOTLIB_AVAILABLE}")
    print()
    
    if _MATPLOTLIB_AVAILABLE:
        print(f"2. Matplotlib可用，应该创建曲线栏目")
        
        # 测试创建应用程序
        app = QApplication(sys.argv)
        from qt_app_v2 import EFileViewer
        
        print(f"3. 创建EFileViewer...")
        viewer = EFileViewer()
        
        print(f"4. 检查曲线tab...")
        curve_tab_found = False
        for i in range(viewer.tab_widget.count()):
            tab_text = viewer.tab_widget.tabText(i)
            print(f"   Tab {i}: {tab_text}")
            if tab_text == "曲线":
                curve_tab_found = True
                print(f"   -> 找到曲线栏目！")
        
        if not curve_tab_found:
            print(f"   -> 错误：曲线栏目未找到！")
            return False
        
        print(f"5. 检查曲线相关组件...")
        attrs = ['curve_section_combo', 'curve_table_combo', 'curve_x_axis_combo', 
                 'curve_y_axis_combo', 'plot_button', 'curve_canvas', 'curve_tab']
        for attr in attrs:
            has_attr = hasattr(viewer, attr)
            status = "存在" if has_attr else "不存在"
            print(f"   {attr}: {status}")
            if not has_attr:
                print(f"   -> 警告：{attr} 不存在！")
                return False
        
        print()
        print(f"="*60)
        print(f"结果：曲线栏目配置正确！")
        print(f"="*60)
        return True
    else:
        print(f"2. Matplotlib不可用，曲线栏目不会创建")
        print(f"   解决方法：安装matplotlib")
        print(f"   命令：pip install matplotlib")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
