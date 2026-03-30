"""
国家电投昆明生产运营中心E文件解析工具 v1.2

本程序用于解析和分析南方电网新能源数据上送规范V3.3版本的E文件数据
支持E文件的选择、解析、数据展示和报告导出功能

作者：陈丰
联系方式：18669061936
版本：1.2
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QTextEdit, QMessageBox, QProgressBar,
                             QGroupBox, QStatusBar, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from efile_parser import parse_efile


class ParseThread(QThread):
    """
    后台解析线程类

    用于在后台线程中执行E文件的解析操作，避免阻塞主UI线程
    继承自QThread，实现了线程安全的解析过程

    信号:
        finished: 解析完成信号，携带解析结果和文件路径
        error: 错误信号，携带错误消息
        progress: 进度信号，携带当前进度百分比
    """

    finished = pyqtSignal(dict, str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, filepath):
        """
        初始化解析线程

        参数:
            filepath: 要解析的E文件路径
        """
        super().__init__()
        self.filepath = filepath

    def run(self):
        """
        线程执行方法，实际执行解析操作

        发送进度信号，调用解析函数，处理结果或错误
        """
        try:
            self.progress.emit(30)
            result = parse_efile(self.filepath)
            self.progress.emit(70)
            self.finished.emit(result, self.filepath)
            self.progress.emit(100)
        except Exception as e:
            self.error.emit(str(e))


class EFileViewer(QMainWindow):
    """
    主窗口类 - E文件查看器

    国家电投昆明生产运营中心E文件解析工具的主界面
    提供文件选择、解析、数据展示和报告导出功能

    属性:
        current_result: 当前解析结果数据
        filepath: 当前选择的文件路径
        thread: 后台解析线程实例
    """

    def __init__(self):
        """
        初始化主窗口

        设置窗口基本属性，初始化UI组件
        """
        super().__init__()
        self.current_result = None
        self.initUI()

    def initUI(self):
        """
        初始化用户界面

        设置窗口标题、大小，创建主布局，并添加所有UI组件：
        - 标题栏（Logo + 标题）
        - 操作按钮（文件选择、解析、导出）
        - 进度条
        - 状态标签
        - 标签页（文件概览、详细数据、原始内容）
        - 状态栏
        """
        self.setWindowTitle("国家电投昆明生产运营中心  E文件解析工具")
        self.setGeometry(100, 100, 1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Header
        header_layout = QHBoxLayout()

        logo_label = QLabel()
        logo_pixmap = QPixmap(r"D:\001\eTextDTA\logo\spic-logo.svg")
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("SPIC")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #E60012; /* SPIC红色 */")
        header_layout.addWidget(logo_label)

        title_layout = QVBoxLayout()

        main_title = QLabel("国家电投昆明生产运营中心   E文件解析工具")
        main_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        main_title.setStyleSheet("color: #e0e0e0; /* 浅灰色文字 */")
        title_layout.addWidget(main_title)

        subtitle = QLabel("根据《南方电网新能源数据上送规范 V3.3修订版（2022.2月）》解析E文件")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignLeft)
        subtitle.setFont(QFont("Microsoft YaHei", 10))
        subtitle.setStyleSheet("color: #b0b0b0; /* 深灰色文字 */")
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("padding: 10px; background: #1a3d1a /* 深绿色背景 */; color: #e0e0e0 /* 浅灰色文字 */; border-radius: 5px; border: 1px solid #00A651 /* SPIC绿色边框 */;")
        self.file_label.setMinimumWidth(300)
        button_layout.addWidget(self.file_label)

        self.browse_button = QPushButton("选择文件")
        self.browse_button.setMinimumWidth(100)
        self.browse_button.setStyleSheet("QPushButton { background-color: #E60012 /* SPIC红色 */; color: white; padding: 8px; border-radius: 5px; } QPushButton:hover { background-color: #FF1A2E /* 浅红色 */; }")
        self.browse_button.clicked.connect(self.browseFile)
        button_layout.addWidget(self.browse_button)

        self.parse_button = QPushButton("解析")
        self.parse_button.setMinimumWidth(100)
        self.parse_button.setEnabled(False)
        self.parse_button.setStyleSheet("QPushButton { background-color: #00A651 /* SPIC绿色 */; color: white; padding: 8px; border-radius: 5px; } QPushButton:hover { background-color: #00C45E /* 浅绿色 */; } QPushButton:disabled { background-color: #ccc /* 灰色 */; }")
        self.parse_button.clicked.connect(self.parseFile)
        button_layout.addWidget(self.parse_button)

        self.export_button = QPushButton("导出报告")
        self.export_button.setMinimumWidth(100)
        self.export_button.setEnabled(False)
        self.export_button.setStyleSheet("QPushButton { background-color: #E60012 /* SPIC红色 */; color: white; padding: 8px; border-radius: 5px; } QPushButton:hover { background-color: #FF1A2E /* 浅红色 */; } QPushButton:disabled { background-color: #ccc /* 灰色 */; }")
        self.export_button.clicked.connect(self.exportReport)
        button_layout.addWidget(self.export_button)

        self.limit_checkbox = QCheckBox("提高性能")
        self.limit_checkbox.setChecked(True)
        self.limit_checkbox.setStyleSheet("color: #e0e0e0; /* 浅灰色文字 */")
        button_layout.addWidget(self.limit_checkbox)

        main_layout.addLayout(button_layout)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { border: 2px solid #E60012 /* SPIC红色 */; border-radius: 5px; text-align: center; } QProgressBar::chunk { background-color: linear-gradient(to right, #E60012 /* SPIC红色 */, #00A651 /* SPIC绿色 */); width: 20px; }")
        main_layout.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("padding: 8px; background: #1a3d1a /* 深绿色背景 */; border-radius: 5px; color: #e0e0e0 /* 浅灰色文字 */; border: 1px solid #00A651 /* SPIC绿色边框 */;")
        main_layout.addWidget(self.status_label)

        # Tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabWidget::pane { border: 2px solid #E60012 /* SPIC红色 */; border-radius: 5px; background: #0d2a0d /* 深绿色背景 */; } QTabBar::tab { background: #1a3d1a /* 深绿色背景 */; color: #e0e0e0 /* 浅灰色文字 */; padding: 10px 20px; margin-right: 2px; } QTabBar::tab:selected { background: linear-gradient(to bottom, #E60012 /* SPIC红色 */, #C4000E /* 深红色 */); color: white; }")
        main_layout.addWidget(self.tab_widget)

        self.summary_tab = QWidget()
        self.initSummaryTab()
        self.tab_widget.addTab(self.summary_tab, "文件概览")

        self.data_tab = QWidget()
        self.initDataTab()
        self.tab_widget.addTab(self.data_tab, "详细数据")

        self.raw_tab = QWidget()
        self.initRawTab()
        self.tab_widget.addTab(self.raw_tab, "原始内容")

        # Status bar
        self.statusBar = QStatusBar()
        self.statusBar.showMessage("国家电投昆明生产运营中心 版权所有 | 版本: 1.2 | 作者：陈丰 联系电话：18669061936")
        self.setStatusBar(self.statusBar)

        self.thread = None

    def initSummaryTab(self):
        """
        初始化文件概览标签页

        创建两个分组框：
        - 文件信息：显示文件基本信息（文件名、解析时间、系统信息等）
        - 统计信息：显示解析结果的统计数据（数据段数量、数据表数量、总数据行数）
        """
        layout = QVBoxLayout(self.summary_tab)

        info_group = QGroupBox("文件信息")
        info_group.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #00A651 /* SPIC绿色 */; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #E60012 /* SPIC红色 */; }")
        info_layout = QVBoxLayout()
        self.info_table = QTableWidget()
        self.info_table.setColumnCount(2)
        self.info_table.setHorizontalHeaderLabels(["参数", "值"])
        self.info_table.horizontalHeader().setStretchLastSection(True)
        info_layout.addWidget(self.info_table)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        stats_group = QGroupBox("统计信息")
        stats_group.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #00A651 /* SPIC绿色 */; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #E60012 /* SPIC红色 */; }")
        stats_layout = QVBoxLayout()
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["统计项", "值"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        stats_layout.addWidget(self.stats_table)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

    def initDataTab(self):
        """
        初始化详细数据标签页

        创建两个表格：
        - section_table: 显示数据段列表（类型、标签、日期、时间）
        - data_table: 显示选中数据段的详细数据内容
        """
        layout = QVBoxLayout(self.data_tab)

        self.section_table = QTableWidget()
        self.section_table.setColumnCount(4)
        self.section_table.setHorizontalHeaderLabels(["类型", "标签", "日期", "时间"])
        self.section_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.section_table.setMaximumHeight(150)
        self.section_table.setStyleSheet("QTableWidget { gridline-color: #00A651 /* SPIC绿色 */; background-color: #0d2a0d /* 深绿色背景 */; color: #e0e0e0 /* 浅灰色文字 */; } QHeaderView::section { background: linear-gradient(to bottom, #E60012 /* SPIC红色 */, #C4000E /* 深红色 */); color: white; padding: 5px; } QTableWidget::item { color: #e0e0e0 /* 浅灰色文字 */; }")
        self.section_table.cellClicked.connect(self.onSectionClicked)
        layout.addWidget(self.section_table)

        self.data_table = QTableWidget()
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setStyleSheet("QTableWidget { gridline-color: #ccc /* 灰色 */; alternate-background-color: #0d2a0d /* 深绿色背景 */; } QHeaderView::section { background: linear-gradient(to bottom, #00A651 /* SPIC绿色 */, #008A43 /* 深绿色 */); color: white; padding: 5px; }")
        layout.addWidget(self.data_table)

    def initRawTab(self):
        """
        初始化原始内容标签页

        创建一个文本编辑器用于显示原始文件内容
        支持多种编码格式，并限制显示长度以提高性能
        """
        layout = QVBoxLayout(self.raw_tab)
        self.raw_text = QTextEdit()
        self.raw_text.setReadOnly(True)
        self.raw_text.setFont(QFont("Consolas", 9))
        self.raw_text.setStyleSheet("QTextEdit { background-color: #0d2a0d /* 深绿 */; border: 1px solid #ccc /* 灰色边框 */; border-radius: 5px; padding: 10px; }")
        layout.addWidget(self.raw_text)

    def browseFile(self):
        """
        文件浏览方法

        弹出文件选择对话框，允许用户选择E文件
        更新文件路径显示，并启用/禁用相关按钮
        """
        filepath, _ = QFileDialog.getOpenFileName(self, "选择E文件", "", "E文件 (*.dat);;所有文件 (*.*)")
        if filepath:
            self.filepath = filepath
            self.file_label.setText(filepath)
            self.parse_button.setEnabled(True)
            self.export_button.setEnabled(False)

    def parseFile(self):
        """
        文件解析方法

        启动后台线程解析选中的E文件
        更新UI状态，显示进度条，禁用操作按钮
        """
        if not hasattr(self, "filepath"):
            return

        self.parse_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在解析文件...")
        self.status_label.setStyleSheet("padding: 8px; background: linear-gradient(to right, #FFF5F5 /* 浅红背景 */, #F0FFF4 /* 浅绿背景 */); border-radius: 5px; color: #E60012 /* SPIC红色 */; border: 1px solid #E60012 /* SPIC红色 */;")

        self.thread = ParseThread(self.filepath)
        self.thread.finished.connect(self.onParseFinished)
        self.thread.error.connect(self.onParseError)
        self.thread.progress.connect(self.onProgress)
        self.thread.start()

    def onProgress(self, value):
        """
        进度更新回调方法

        更新进度条显示

        参数:
            value: 当前进度百分比
        """
        self.progress_bar.setValue(value)

    def onParseFinished(self, result, filepath):
        """
        解析完成回调方法

        处理解析成功的结果，更新UI显示，启用操作按钮

        参数:
            result: 解析结果数据
            filepath: 解析的文件路径
        """
        try:
            self.current_result = result
            self.progress_bar.setVisible(False)
            self.status_label.setText("解析完成！")
            self.status_label.setStyleSheet("padding: 8px; background: linear-gradient(to right, #F0FFF4 /* 浅绿背景 */, #E6FFED /* 浅绿背景 */); border-radius: 5px; color: #00A651 /* SPIC绿色 */; border: 1px solid #00A651 /* SPIC绿色 */;")

            self.displaySummary(result)
            self.displayDataSections(result)
            self.displayRaw(result)

            self.parse_button.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.export_button.setEnabled(True)
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_label.setText("显示数据时出错: " + str(e))
            self.status_label.setStyleSheet("padding: 8px; background: linear-gradient(to right, #FFF5F5 /* 浅红背景 */, #FFE5E5 /* 浅红背景 */); border-radius: 5px; color: #E60012 /* SPIC红色 */; border: 1px solid #E60012 /* SPIC红色 */;")
            QMessageBox.critical(self, "显示错误", "解析成功但显示数据时出错:\n" + str(e))
            self.parse_button.setEnabled(True)
            self.browse_button.setEnabled(True)

    def onParseError(self, error_msg):
        """
        解析错误回调方法

        处理解析失败的情况，显示错误信息，恢复UI状态

        参数:
            error_msg: 错误消息
        """
        self.progress_bar.setVisible(False)
        self.status_label.setText("解析失败: " + error_msg)
        self.status_label.setStyleSheet("padding: 8px; background: linear-gradient(to right, #FFF5F5 /* 浅红背景 */, #FFE5E5 /* 浅红背景 */); border-radius: 5px; color: #E60012 /* SPIC红色 */; border: 1px solid #E60012 /* SPIC红色 */;")
        QMessageBox.critical(self, "解析错误", "解析E文件时出错:\n" + error_msg)
        self.parse_button.setEnabled(True)
        self.browse_button.setEnabled(True)

    def displaySummary(self, result):
        self.info_table.setRowCount(0)
        self.info_table.setRowCount(6)

        self.info_table.setItem(0, 0, QTableWidgetItem("文件名"))
        self.info_table.setItem(0, 1, QTableWidgetItem(os.path.basename(result["filename"])))

        self.info_table.setItem(1, 0, QTableWidgetItem("解析时间"))
        self.info_table.setItem(1, 1, QTableWidgetItem(result["parse_time"]))

        self.info_table.setItem(2, 0, QTableWidgetItem("System"))
        self.info_table.setItem(2, 1, QTableWidgetItem(result["header"].get("System", "N/A")))

        self.info_table.setItem(3, 0, QTableWidgetItem("Version"))
        self.info_table.setItem(3, 1, QTableWidgetItem(result["header"].get("Version", "N/A")))

        self.info_table.setItem(4, 0, QTableWidgetItem("Code"))
        self.info_table.setItem(4, 1, QTableWidgetItem(result["header"].get("Code", "N/A")))

        self.info_table.setItem(5, 0, QTableWidgetItem("Data"))
        self.info_table.setItem(5, 1, QTableWidgetItem(result["header"].get("Data", "N/A")))

        total_sections = len(result["sections"])
        total_tables = sum(len(s["tables"]) for s in result["sections"])
        total_rows = sum(sum(t["row_count"] for t in s["tables"]) for s in result["sections"])

        self.stats_table.setRowCount(0)
        self.stats_table.setRowCount(3)

        self.stats_table.setItem(0, 0, QTableWidgetItem("数据段数量"))
        self.stats_table.setItem(0, 1, QTableWidgetItem(str(total_sections)))

        self.stats_table.setItem(1, 0, QTableWidgetItem("数据表数量"))
        self.stats_table.setItem(1, 1, QTableWidgetItem(str(total_tables)))

        self.stats_table.setItem(2, 0, QTableWidgetItem("总数据行数"))
        self.stats_table.setItem(2, 1, QTableWidgetItem(str(total_rows)))

    def displayDataSections(self, result):
        self.section_table.setRowCount(0)
        self.section_table.setRowCount(len(result["sections"]))

        for idx, section in enumerate(result["sections"]):
            self.section_table.setItem(idx, 0, QTableWidgetItem(section["type"]))
            self.section_table.setItem(idx, 1, QTableWidgetItem(section["tag"]))
            self.section_table.setItem(idx, 2, QTableWidgetItem(section["date"]))
            self.section_table.setItem(idx, 3, QTableWidgetItem(section["time"]))

        if len(result["sections"]) > 0:
            self.section_table.selectRow(0)
            self.onSectionClicked(0, 0)

    def onSectionClicked(self, row, column):
        if self.current_result is None or row >= len(self.current_result["sections"]):
            return

        section = self.current_result["sections"][row]

        if len(section["tables"]) == 0:
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            self.status_label.setText("该数据段没有数据表")
            return

        table = section["tables"][0]
        header_count = len(table["header"])
        row_count = len(table["rows"])

        self.data_table.setColumnCount(header_count)
        self.data_table.setHorizontalHeaderLabels(table["header"])

        if self.limit_checkbox.isChecked():
            max_display_rows = min(row_count, 1000)
        else:
            max_display_rows = row_count

        self.data_table.setRowCount(max_display_rows)

        for row_idx in range(max_display_rows):
            row_data = table["rows"][row_idx]
            for col_idx, header in enumerate(table["header"]):
                value = row_data.get(header, "")
                self.data_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        if row_count > max_display_rows:
            self.status_label.setText("已显示 " + str(max_display_rows) + " 行 (共 " + str(row_count) + " 行，限制显示以提高性能)")
        else:
            self.status_label.setText("已加载 " + str(row_count) + " 行数据")

    def displayRaw(self, result):
        encodings = ["utf-8", "gbk", "gb2312", "gb18030", "utf-16"]
        content = None

        for encoding in encodings:
            try:
                with open(result["filename"], "r", encoding=encoding) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, UnicodeError, LookupError):
                continue

        if content is None:
            content = "无法读取文件内容：不支持的文件编码"

        max_length = 100000
        if len(content) > max_length:
            content = content[:max_length] + "\n\n... (内容已截断，原始文件大小: " + str(len(content)) + " 字节)"

        self.raw_text.setPlainText(content)

    def exportReport(self):
        if self.current_result is None:
            return

        filepath, _ = QFileDialog.getSaveFileName(self, "保存报告", "", "文本文件 (*.txt);;所有文件 (*.*)")

        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("=" * 60 + "\n")
                    f.write("国家电投昆明生产运营中心E文件解析报告\n")
                    f.write("版本: 1.2\n")
                    f.write("=" * 60 + "\n\n")

                    f.write("文件信息:\n")
                    f.write("  文件名: " + os.path.basename(self.current_result["filename"]) + "\n")
                    f.write("  解析时间: " + self.current_result["parse_time"] + "\n\n")

                    f.write("系统信息:\n")
                    for key, value in self.current_result["header"].items():
                        f.write("  " + key + ": " + str(value) + "\n")
                    f.write("\n")

                    f.write("统计信息:\n")
                    total_sections = len(self.current_result["sections"])
                    total_tables = sum(len(s["tables"]) for s in self.current_result["sections"])
                    total_rows = sum(sum(t["row_count"] for t in s["tables"]) for s in self.current_result["sections"])
                    f.write("  数据段数量: " + str(total_sections) + "\n")
                    f.write("  数据表数量: " + str(total_tables) + "\n")
                    f.write("  总数据行数: " + str(total_rows) + "\n\n")

                    for idx, section in enumerate(self.current_result["sections"], 1):
                        f.write("-" * 60 + "\n")
                        f.write("数据段 " + str(idx) + ": " + section["type"] + "\n")
                        f.write("  标签: " + section["tag"] + "\n")
                        f.write("  场站: " + section["station"] + "\n")
                        f.write("  日期: " + section["date"] + "\n")
                        f.write("  时间: " + section["time"] + "\n")
                        f.write("  数据表数量: " + str(len(section["tables"])) + "\n\n")

                        for table_idx, table in enumerate(section["tables"], 1):
                            f.write("  数据表 " + str(table_idx) + " (" + str(table["row_count"]) + " 行):\n")
                            f.write("    表头: " + ", ".join(table["header"]) + "\n\n")

                            if table["row_count"] <= 10:
                                for row_idx, row_data in enumerate(table["rows"], 1):
                                    f.write("    行 " + str(row_idx) + ": ")
                                    row_str = ", ".join([h + "=" + str(row_data.get(h, "")) for h in table["header"]])
                                    f.write(row_str + "\n")
                            else:
                                for row_idx, row_data in enumerate(table["rows"][:5], 1):
                                    f.write("    行 " + str(row_idx) + ": ")
                                    row_str = ", ".join([h + "=" + str(row_data.get(h, "")) for h in table["header"]])
                                    f.write(row_str + "\n")
                                f.write("    ... 还有 " + str(table["row_count"] - 5) + " 行\n\n")

                    f.write("=" * 60 + "\n")
                    f.write("国家电投昆明生产运营中心 版权所有\n")
                    f.write("版本: 1.2\n")
                    f.write("作者：陈丰 联系电话：18669061936\n")
                    f.write("报告生成完成\n")
                    f.write("=" * 60 + "\n")

                QMessageBox.information(self, "成功", "报告已成功导出！")
            except Exception as e:
                QMessageBox.critical(self, "错误", "导出失败:\n" + str(e))


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyle("Windows")

    viewer = EFileViewer()
    viewer.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
