# -*- coding: utf-8 -*-
"""
E文件解析工具 - PySide6 版本 v2.0.0
国家电投昆明生产运营中心 版权所有
作者: 陈丰 联系电话: 0871-65666603
"""

import sys
import os
import sqlite3
import json
import winreg
import tarfile
import tempfile
import shutil
from datetime import datetime

# Lite 版本：不包含曲线功能，减小体积
_MATPLOTLIB_AVAILABLE = False
FigureCanvas = None
Figure = None

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QTableWidget, QTableWidgetItem, QTabWidget,
    QTextEdit, QMessageBox, QProgressBar,
    QGroupBox, QStatusBar, QCheckBox, QComboBox, QDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap

from efile_parser import parse_efile
from db_utils import init_db, save_result, query_results

LOGO_PATH = r"D:\001\eTextDTA\logo\spic-logo.svg"
DB_PATH = r"D:/001/eText/eparser.db"

# --------------- 解析线程 ----------------
class ParseThread(QThread):
    finished = Signal(dict, str)
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

    def run(self):
        try:
            self.progress.emit(30)
            result = parse_efile(self.filepath)
            self.progress.emit(70)
            self.finished.emit(result, self.filepath)
            self.progress.emit(100)
        except Exception as e:
            self.error.emit(str(e))

# --------------- 主界面 ---------------
class EFileViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_result = None
        self.current_theme = "light"

        self.initUI()
        self.apply_theme()

    def initUI(self):
        self.setWindowTitle("南网102-e文件解析工具")
        self.setGeometry(100, 100, 1024, 768)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)

        # Header（Logo + 标题）
        header_layout = QHBoxLayout()

        self.logo_label = QLabel()
        if os.path.exists(LOGO_PATH):
            try:
                logo_pixmap = QPixmap(LOGO_PATH)
                if not logo_pixmap.isNull():
                    logo_pixmap = logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.logo_label.setPixmap(logo_pixmap)
            except Exception:
                self.logo_label.setText("SPIC")
                self.logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #E60012;")
        else:
            self.logo_label.setText("SPIC")
            self.logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #E60012;")
        header_layout.addWidget(self.logo_label)

        title_layout = QVBoxLayout()
        self.main_title = QLabel("国家电投昆明生产运营中心 南网102-e文件解析工具")
        self.main_title.setAlignment(Qt.AlignLeft)
        self.main_title.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_layout.addWidget(self.main_title)

        self.subtitle = QLabel("根据《南方电网新能源数据上送规范V3.3修订版》解析e文件")
        self.subtitle.setAlignment(Qt.AlignLeft)
        self.subtitle.setFont(QFont("Microsoft YaHei", 10))
        title_layout.addWidget(self.subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        # Buttons Row
        button_layout = QHBoxLayout()

        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet(
            "padding: 10px; background: #1b1b1b; color: #e0e0e0; border-radius: 5px; border: 1px solid #2a2a2a;"
        )
        self.file_label.setMinimumWidth(300)
        button_layout.addWidget(self.file_label)

        self.browse_button = QPushButton("选择文件")
        self.browse_button.setMinimumWidth(100)
        self.browse_button.clicked.connect(self.browseFile)
        button_layout.addWidget(self.browse_button)

        self.parse_button = QPushButton("解析")
        self.parse_button.setMinimumWidth(100)
        self.parse_button.setEnabled(False)
        self.parse_button.clicked.connect(self.parseFile)
        button_layout.addWidget(self.parse_button)

        self.export_button = QPushButton("导出报告")
        self.export_button.setMinimumWidth(100)
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.exportReport)
        button_layout.addWidget(self.export_button)

        self.limit_checkbox = QCheckBox("限制显示(提高性能)")
        self.limit_checkbox.setChecked(True)
        button_layout.addWidget(self.limit_checkbox)

        self.main_layout.addLayout(button_layout)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.main_layout.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("padding: 8px; background: #f9f9f9; border-radius: 5px; border: 1px solid #d0d0d0;")
        self.main_layout.addWidget(self.status_label)

        # Tabs
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.summary_tab = QWidget()
        self.initSummaryTab()
        self.tab_widget.addTab(self.summary_tab, "文件概览")

        self.data_tab = QWidget()
        self.initDataTab()
        self.tab_widget.addTab(self.data_tab, "详细数据")

        self.raw_tab = QWidget()
        self.initRawTab()
        self.tab_widget.addTab(self.raw_tab, "原始内容")

        # Curve Tab (only if Matplotlib is available)
        if _MATPLOTLIB_AVAILABLE:
            self.curve_tab = QWidget()
            self.initCurveTab()
            self.tab_widget.addTab(self.curve_tab, "曲线")
            # Curve data storage for quick refresh
            self.curve_section_combo.currentIndexChanged.connect(self._update_curve_table_and_axes)
            self.curve_table_combo.currentIndexChanged.connect(self._update_curve_table_and_axes)
        else:
            print("Matplotlib not available, curve tab will not be created")

        # Status bar
        self.statusBar = QStatusBar()
        self.statusBar.showMessage("国家电投昆明生产运营中心 版权所有 | Ver: 2.0 | 联系电话: 0871-65666603")
        self.setStatusBar(self.statusBar)

        self.thread = None

        # Theme check timer
        self.theme_timer = QTimer()
        self.theme_timer.timeout.connect(self.check_theme_change)
        self.theme_timer.start(5000)

    # -------------- 主题 --------------
    def apply_theme(self):
        self.current_theme = get_windows_theme()
        stylesheet = get_theme_stylesheet(self.current_theme)
        self.setStyleSheet(stylesheet)

    def check_theme_change(self):
        new_theme = get_windows_theme()
        if new_theme != self.current_theme:
            self.apply_theme()

    # -------------- Tab: Summary --------------
    def initSummaryTab(self):
        layout = QVBoxLayout(self.summary_tab)

        info_group = QGroupBox("文件信息")
        info_layout = QVBoxLayout()
        self.info_table = QTableWidget()
        self.info_table.setColumnCount(2)
        self.info_table.setHorizontalHeaderLabels(["参数", "值"])
        self.info_table.horizontalHeader().setStretchLastSection(True)
        info_layout.addWidget(self.info_table)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        stats_group = QGroupBox("统计信息")
        stats_layout = QVBoxLayout()
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["统计项", "值"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        stats_layout.addWidget(self.stats_table)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

    # -------------- Tab: Data --------------
    def initDataTab(self):
        layout = QVBoxLayout(self.data_tab)

        self.section_table = QTableWidget()
        self.section_table.setColumnCount(4)
        self.section_table.setHorizontalHeaderLabels(["类型", "标签", "日期", "时间"])
        self.section_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.section_table.setMaximumHeight(150)
        self.section_table.cellClicked.connect(self.onSectionClicked)
        layout.addWidget(self.section_table)

        self.data_table = QTableWidget()
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setAlternatingRowColors(True)
        layout.addWidget(self.data_table)

    # -------------- Tab: Raw --------------
    def initRawTab(self):
        layout = QVBoxLayout(self.raw_tab)
        self.raw_text = QTextEdit()
        self.raw_text.setReadOnly(True)
        self.raw_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.raw_text)

    # -------------- Tab: Curve (新增) --------------
    def initCurveTab(self):
        layout = QVBoxLayout(self.curve_tab)

        # Controls
        control = QHBoxLayout()
        control.addWidget(QLabel("数据段:"))
        self.curve_section_combo = QComboBox()
        control.addWidget(self.curve_section_combo)

        control.addWidget(QLabel("数据表:"))
        self.curve_table_combo = QComboBox()
        control.addWidget(self.curve_table_combo)

        control.addWidget(QLabel("X 轴:"))
        self.curve_x_axis_combo = QComboBox()
        control.addWidget(self.curve_x_axis_combo)

        control.addWidget(QLabel("Y 轴:"))
        self.curve_y_axis_combo = QComboBox()
        control.addWidget(self.curve_y_axis_combo)

        self.plot_button = QPushButton("绘制曲线")
        self.plot_button.clicked.connect(self.plotCurve)
        control.addWidget(self.plot_button)

        control.addStretch()
        layout.addLayout(control)

        # Canvas
        if _MATPLOTLIB_AVAILABLE and FigureCanvas is not None and Figure is not None:
            try:
                self.curve_canvas = FigureCanvas(Figure(figsize=(10, 6)))
                layout.addWidget(self.curve_canvas)
                self._curve_plot_available = True
            except Exception as e:
                print(f"Failed to create Matplotlib canvas: {e}")
                layout.addWidget(QLabel("Matplotlib 未安装，曲线绘制不可用"))
                self.curve_canvas = None
                self._curve_plot_available = False
        else:
            layout.addWidget(QLabel("Matplotlib 未安装，曲线绘制不可用"))
            self.curve_canvas = None
            self._curve_plot_available = False

        self.curve_preview_info = QLabel()
        self.curve_preview_info.setText("曲线选项将随解析结果填充")
        layout.addWidget(self.curve_preview_info)

    # 更新曲线相关选项
    def updateCurveOptions(self):
        if not hasattr(self, "current_result") or self.current_result is None:
            self.curve_section_combo.clear()
            self.curve_table_combo.clear()
            self.curve_x_axis_combo.clear()
            self.curve_y_axis_combo.clear()
            return

        sections = self.current_result.get("sections", [])
        self.curve_section_combo.clear()
        for idx, s in enumerate(sections):
            self.curve_section_combo.addItem(f"{idx+1}. {s['tag']} ({s['type']})", idx)

        if sections:
            self.curve_section_combo.setCurrentIndex(0)
            self._update_curve_table_and_axes()

    def _update_curve_table_and_axes(self):
        if not self.current_result:
            return
        si = self.curve_section_combo.currentData()
        if si is None or si >= len(self.current_result["sections"]):
            return
        section = self.current_result["sections"][si]

        # Block signals to prevent recursion
        self.curve_table_combo.blockSignals(True)
        self.curve_section_combo.blockSignals(True)

        self.curve_table_combo.clear()
        for j, tbl in enumerate(section["tables"]):
            self.curve_table_combo.addItem(f"表 {j+1} - {tbl['row_count']} 行", j)

        if section["tables"]:
            self.curve_table_combo.setCurrentIndex(0)
            headers = section["tables"][0]["header"]
            self.curve_x_axis_combo.clear()
            self.curve_y_axis_combo.clear()
            for h in headers:
                self.curve_x_axis_combo.addItem(h)
                self.curve_y_axis_combo.addItem(h)
        else:
            self.curve_x_axis_combo.clear()
            self.curve_y_axis_combo.clear()

        # Unblock signals
        self.curve_table_combo.blockSignals(False)
        self.curve_section_combo.blockSignals(False)

    # 绘制曲线
    def plotCurve(self):
        if getattr(self, "current_result", None) is None:
            QMessageBox.warning(self, "警告", "请先解析文件")
            return
        if not self._curve_plot_available or self.curve_canvas is None:
            QMessageBox.warning(self, "警告", "Matplotlib 未安装，无法绘制曲线")
            return

        try:
            section_idx = self.curve_section_combo.currentIndex()
            table_idx = self.curve_table_combo.currentIndex()
            x_axis = self.curve_x_axis_combo.currentText()
            y_axis = self.curve_y_axis_combo.currentText()

            sections = self.current_result["sections"]
            if section_idx < 0 or section_idx >= len(sections):
                QMessageBox.warning(self, "警告", "选择的数据段不存在")
                return
            section = sections[section_idx]
            if table_idx < 0 or table_idx >= len(section["tables"]):
                QMessageBox.warning(self, "警告", "选择的数据表不存在")
                return
            table = section["tables"][table_idx]
            if x_axis not in table["header"] or y_axis not in table["header"]:
                QMessageBox.warning(self, "警告", "选择的字段不存在")
                return

            x_values, y_values = [], []
            for row in table["rows"]:
                try:
                    xv = float(str(row.get(x_axis, "0")).strip())
                    yv = float(str(row.get(y_axis, "0")).strip())
                    x_values.append(xv)
                    y_values.append(yv)
                except (ValueError, AttributeError):
                    continue

            if not x_values or not y_values:
                QMessageBox.warning(self, "警告", "无法提取有效数据")
                return

            fig = self.curve_canvas.figure
            fig.clear()
            ax = fig.add_subplot(111)
            ax.plot(x_values, y_values, 'b-', linewidth=1.5, label=f'{y_axis} vs {x_axis}')
            ax.set_xlabel(x_axis, fontsize=10)
            ax.set_ylabel(y_axis, fontsize=10)
            ax.set_title(f'曲线图表 - {section["tag"]}', fontsize=12, fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend()
            self.curve_canvas.draw()
            self.status_label.setText(f"曲线绘制完成: {len(x_values)} 个数据点")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"绘制曲线时出错:\n{str(e)}")

    # -------------- Raw 内容显示改造 --------------
    def displayRaw(self, result):
        # tar.gz 的解压内容预览
        if "tar_info" in result and result["tar_info"]:
            tar_info = result["tar_info"]
            tar_name = tar_info.get("tar_name", "")
            dat_count = tar_info.get("dat_count", 0)
            previews = tar_info.get("preview", [])

            content = "= tar.gz 文件信息 =\n"
            content += f"文件名: {tar_name}\n"
            content += f"包含 .dat 文件数: {dat_count}\n\n"
            content += "= 数据段信息 =\n"
            content += f"总数据段数: {len(result['sections'])}\n\n"
            content += "= 解压内容预览 =\n"
            if previews:
                for line in previews:
                    content += line + "\n"
            else:
                content += "(无预览内容)\n"

            for idx, section in enumerate(result["sections"], 1):
                content += f"[{idx}] 数据段: {section['tag']} - 类型: {section['type']}\n"
                content += f"    日期: {section['date']} 时间: {section['time']}\n"

            self.raw_text.setPlainText(content)
            return

        # 普通 .dat 文件显示
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

    # -------------- 导出 --------------
    def exportReport(self):
        if self.current_result is None:
            return

        filepath, _ = QFileDialog.getSaveFileName(self, "保存报告", "", "文本文件 (*.txt);;所有文件 (*.*)")

        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("=" * 60 + "\n")
                    f.write("e文件解析工具解析报告\n")
                    f.write("版本: 2.0.0\n")
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
                    f.write("版本: 2.0.0\n")
                    f.write("作者：陈丰 电话：0871-65666603\n")
                    f.write("报告生成完成\n")
                    f.write("=" * 60 + "\n")

                QMessageBox.information(self, "成功", "报告已成功导出！")
            except Exception as e:
                QMessageBox.critical(self, "错误", "导出失败:\n" + str(e))

    # -------------- 文件浏览 --------------
    def browseFile(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "选择E文件", "", "E文件 (*.tar.gz);;E文件 (*.dat);;所有文件 (*.*)")
        if filepath:
            self.filepath = filepath
            self.file_label.setText(filepath)
            self.parse_button.setEnabled(True)
            self.export_button.setEnabled(False)

    # -------------- 文件解析 --------------
    def parseFile(self):
        if not hasattr(self, "filepath"):
            return

        self.parse_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在解析文件...")
        self.status_label.setStyleSheet("padding: 8px; background: #f0f0f0; border-radius: 5px; border: 1px solid #d0d0d0;")

        self.thread = ParseThread(self.filepath)
        self.thread.finished.connect(self.onParseFinished)
        self.thread.error.connect(self.onParseError)
        self.thread.progress.connect(self.onProgress)
        self.thread.start()

    # -------------- 解析进度 --------------
    def onProgress(self, value):
        self.progress_bar.setValue(value)

    # -------------- 解析错误 --------------
    def onParseError(self, error_msg):
        self.progress_bar.setVisible(False)
        self.status_label.setText("解析失败: " + error_msg)
        self.status_label.setStyleSheet("padding: 8px; background: #ffebee; border-radius: 5px; border: 1px solid #ef9a9a;")
        QMessageBox.critical(self, "解析错误", "解析E文件时出错:\n" + error_msg)
        self.parse_button.setEnabled(True)
        self.browse_button.setEnabled(True)

    # -------------- 解析完成 --------------
    def onParseFinished(self, result, filepath):
        try:
            self.current_result = result
            self.progress_bar.setVisible(False)
            self.status_label.setText("解析完成！")
            self.status_label.setStyleSheet("padding: 8px; background: #e8f5e9; border-radius: 5px; border: 1px solid #a5d6a7;")

            self.displaySummary(result)
            self.displayDataSections(result)
            self.displayRaw(result)
            # Only update curve options if matplotlib is available
            if _MATPLOTLIB_AVAILABLE:
                self.updateCurveOptions()

            self.parse_button.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.export_button.setEnabled(True)
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_label.setText("显示数据时出错: " + str(e))
            self.status_label.setStyleSheet("padding: 8px; background: #ffebee; border-radius: 5px; border: 1px solid #ef9a9a;")
            QMessageBox.critical(self, "显示错误", "解析成功但显示数据时出错:\n" + str(e))
            self.parse_button.setEnabled(True)
            self.browse_button.setEnabled(True)

    # -------------- 显示摘要信息 --------------
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

    # -------------- 显示数据段 --------------
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

    # -------------- 处理段点击 --------------
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

    # -------------- 运行入口 --------------
def get_windows_theme() -> str:
    """获取 Windows 系统主题设置 (light/dark)"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if value == 1 else "dark"
    except Exception:
        return "light"

def get_theme_stylesheet(theme: str) -> str:
    """返回对应主题的样式表"""
    if theme == "dark":
        return """
        QMainWindow { background-color: #1e1e1e; color: #e0e0e0; }
        QWidget { background-color: #1e1e1e; color: #e0e0e0; }
        QLabel { color: #e0e0e0; }
        QTableWidget { background-color: #2d2d2d; color: #e0e0e0; gridline-color: #3d3d3d; }
        QTableWidget::item:selected { background-color: #0078d4; color: white; }
        QHeaderView::section { background-color: #0078d4; color: white; padding: 5px; border: 1px solid #005a9e; }
        QPushButton { background-color: #0078d4; color: white; padding: 8px; border-radius: 5px; }
        QPushButton:hover { background-color: #1e8ad6; }
        QPushButton:disabled { background-color: #4a4a4a; color: #808080; }
        QProgressBar { border: 2px solid #3d3d3d; border-radius: 5px; background-color: #2d2d2d; color: #e0e0e0; }
        QProgressBar::chunk { background-color: #0078d4; }
        QTabWidget::pane { border: 2px solid #3d3d3d; background-color: #2d2d2d; }
        QTabBar::tab { background-color: #2d2d2d; color: #e0e0e0; padding: 10px 20px; }
        QTabBar::tab:selected { background-color: #0078d4; color: white; }
        QGroupBox { border: 2px solid #3d3d3d; border-radius: 5px; margin-top: 10px; color: #e0e0e0; font-weight: bold; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        QTextEdit { background-color: #1e1e1e; color: #e0e0e0; border: 1px solid #3d3d3d; border-radius: 5px; padding: 10px; font-family: "Consolas"; }
        QStatusBar { background-color: #0078d4; color: white; }
        """
    else:
        return """
        QMainWindow { background-color: #ffffff; color: #000; }
        QWidget { background-color: #ffffff; color: #000; }
        QLabel { color: #000; }
        QTableWidget { background-color: #ffffff; color: #000; gridline-color: #d0d0d0; }
        QTableWidget::item:selected { background-color: #0078d4; color: white; }
        QHeaderView::section { background-color: #0078d4; color: white; padding: 5px; border: 1px solid #005a9e; }
        QPushButton { background-color: #0078d4; color: white; padding: 8px; border-radius: 5px; }
        QPushButton:hover { background-color: #1e8ad6; }
        QPushButton:disabled { background-color: #d0d0d0; color: #808080; }
        QProgressBar { border: 2px solid #d0d0d0; border-radius: 5px; text-align: center; background-color: #fff; color: #000; }
        QProgressBar::chunk { background-color: #0078d4; }
        QTabWidget::pane { border: 2px solid #d0d0d0; background-color: #fff; }
        QTabBar::tab { background-color: #f0f0f0; color: #000; padding: 10px 20px; border: 1px solid #d0d0d0; border-bottom: none; border-top-left-radius: 5px; border-top-right-radius: 5px; }
        QTabBar::tab:selected { background-color: #0078d4; color: white; }
        QGroupBox { border: 2px solid #d0d0d0; border-radius: 5px; margin-top: 10px; color: #000; font-weight: bold; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        QTextEdit { background-color: #fff; color: #000; border: 1px solid #d0d0d0; border-radius: 5px; padding: 10px; font-family: "Consolas"; }
        QStatusBar { background-color: #0078d4; color: white; }
        """

def main():
    # 初始化数据库
    init_db()

    # Check for existing QApplication instance
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
    else:
        # Reuse existing instance
        print("Reusing existing QApplication instance")

    viewer = EFileViewer()
    viewer.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
