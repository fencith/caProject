# -*- coding: utf-8 -*-
"""
最终验证脚本 - 确认曲线栏目存在且功能正常
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from qt_app_v2 import EFileViewer, _MATPLOTLIB_AVAILABLE
from efile_parser import parse_efile

class FinalTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("曲线栏目最终验证")
        self.setGeometry(300, 300, 600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 1. 环境检查
        label1 = QLabel("=== 环境检查 ===")
        label1.setStyleSheet("font-weight: bold;")
        layout.addWidget(label1)
        
        matplot_status = "可用 [OK]" if _MATPLOTLIB_AVAILABLE else "不可用 [FAIL]"
        label2 = QLabel(f"Matplotlib: {matplot_status}")
        layout.addWidget(label2)
        
        # 2. 创建应用程序
        self.app_viewer = EFileViewer()
        
        # 3. 检查Tab
        label3 = QLabel("\n=== Tab检查 ===")
        label3.setStyleSheet("font-weight: bold;")
        layout.addWidget(label3)
        
        tab_count = self.app_viewer.tab_widget.count()
        label4 = QLabel(f"Tab总数: {tab_count}")
        layout.addWidget(label4)
        
        tabs_info = ""
        for i in range(tab_count):
            tab_text = self.app_viewer.tab_widget.tabText(i)
            tabs_info += f"Tab {i}: {tab_text}\n"
        
        label5 = QLabel(tabs_info)
        layout.addWidget(label5)
        
        # 4. 曲线栏目检查
        curve_found = "曲线" in [self.app_viewer.tab_widget.tabText(i) for i in range(tab_count)]
        curve_status = "存在 [OK]" if curve_found else "不存在 [FAIL]"
        label6 = QLabel(f"曲线栏目: {curve_status}")
        if curve_found:
            label6.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
        else:
            label6.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        layout.addWidget(label6)
        
        # 5. 曲线组件检查
        label7 = QLabel("\n=== 曲线组件检查 ===")
        label7.setStyleSheet("font-weight: bold;")
        layout.addWidget(label7)
        
        curve_attrs = ['curve_section_combo', 'curve_table_combo', 'curve_x_axis_combo',
                      'curve_y_axis_combo', 'plot_button', 'curve_canvas', 'curve_tab']
        all_attrs_ok = True
        for attr in curve_attrs:
            has_attr = hasattr(self.app_viewer, attr)
            status = "[OK]" if has_attr else "[FAIL]"
            label_attr = QLabel(f"  {attr}: {status}")
            if not has_attr:
                label_attr.setStyleSheet("color: red;")
            layout.addWidget(label_attr)
            if not has_attr:
                all_attrs_ok = False
        
        # 6. 测试文件解析
        label8 = QLabel("\n=== 测试文件解析 ===")
        label8.setStyleSheet("font-weight: bold;")
        layout.addWidget(label8)
        
        test_file = r"D:\001\eText\102E文本数据202601\DZL_DQYC_202601.tar.gz"
        try:
            result = parse_efile(test_file)
            self.app_viewer.current_result = result
            sections_count = len(result.get("sections", []))
            label9 = QLabel(f"文件解析成功，数据段: {sections_count}")
            label9.setStyleSheet("color: green;")
            layout.addWidget(label9)
            
            # 测试updateCurveOptions
            if _MATPLOTLIB_AVAILABLE:
                self.app_viewer.updateCurveOptions()
                label10 = QLabel("updateCurveOptions调用成功 [OK]")
                label10.setStyleSheet("color: green;")
                layout.addWidget(label10)
            else:
                label10 = QLabel("Matplotlib不可用，跳过updateCurveOptions [SKIP]")
                layout.addWidget(label10)
        except Exception as e:
            label11 = QLabel(f"文件解析失败: {e}")
            label11.setStyleSheet("color: red;")
            layout.addWidget(label11)
        
        # 7. 打开完整应用按钮
        btn = QPushButton("打开完整应用程序")
        btn.clicked.connect(self.open_full_app)
        btn.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold;")
        layout.addWidget(btn)
        
        # 8. 总结
        all_ok = _MATPLOTLIB_AVAILABLE and curve_found and all_attrs_ok
        summary = "\n=== 总结 ===\n"
        if all_ok:
            summary += "[OK] 曲线栏目配置正确且功能正常！\n\n"
            summary += "请点击上方按钮打开完整应用程序\n"
            summary += "然后查看'曲线'Tab（应该是第4个Tab）"
        else:
            summary += "[FAIL] 检查发现问题！\n\n"
            summary += "请运行以下命令进行详细诊断：\n"
            summary += "python diagnose_curve_issue.py"
        
        label12 = QLabel(summary)
        if all_ok:
            label12.setStyleSheet("background-color: #e8f5e9; padding: 10px; border-radius: 5px; color: green; font-weight: bold;")
        else:
            label12.setStyleSheet("background-color: #ffebee; padding: 10px; border-radius: 5px; color: red; font-weight: bold;")
        layout.addWidget(label12)
        
        self.layout().addStretch()
    
    def open_full_app(self):
        """打开完整应用程序"""
        full_app = EFileViewer()
        full_app.setWindowTitle("e文件解析工具 v2.0.0")
        full_app.setGeometry(100, 100, 1400, 900)
        full_app.show()

def main():
    app = QApplication(sys.argv)
    window = FinalTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
