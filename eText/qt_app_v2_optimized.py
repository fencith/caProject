# -*- coding: utf-8 -*-
"""
E文件解析工具 - PySide6 优化版本 v2.2.0
国家电投云南国际昆明生产运营中心 版权所有
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
    QGroupBox, QStatusBar, QCheckBox, QComboBox, QDialog, QSplitter,
    QSizePolicy, QSpacerItem, QFrame, QToolBar, QMenuBar,
    QMenu, QHeaderView, QAbstractItemView, QItemDelegate, QLineEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize
from PySide6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QBrush, QLinearGradient, QPainter, QPen

from efile_parser import parse_efile
from db_utils import init_db, save_result, query_results

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，适用于开发和打包环境"""
    if getattr(sys, 'frozen', False):
        # 打包后的exe
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

# 获取exe所在目录的路径（适用于打包后的exe）
if getattr(sys, 'frozen', False):
    # 打包后的exe
    APP_DIR = os.path.dirname(sys.executable)
else:
    # 开发环境
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 使用相对路径以便打包
LOGO_PATH = get_resource_path("spic_logo.png")
DB_PATH = os.path.join(APP_DIR, "eparser.db")

# --------------- 数据库管理对话框 ----------------
class DatabaseManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("数据库管理")
        self.setGeometry(200, 200, 1000, 700)
        self.setWindowIcon(QIcon(get_resource_path("spic_logo.png")))
        # 添加窗口标志，包含最大化和最小化按钮
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 按钮行
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.refresh_button = QPushButton("刷新列表")
        self.refresh_button.setIcon(QIcon.fromTheme("view-refresh", QIcon(get_resource_path("refresh.png"))))
        self.refresh_button.setMinimumHeight(35)
        self.refresh_button.clicked.connect(self.loadDatabaseRecords)
        button_layout.addWidget(self.refresh_button)

        self.delete_button = QPushButton("删除选中")
        self.delete_button.setIcon(QIcon.fromTheme("edit-delete", QIcon(get_resource_path("delete.png"))))
        self.delete_button.setMinimumHeight(35)
        self.delete_button.clicked.connect(self.deleteSelectedRecords)
        button_layout.addWidget(self.delete_button)

        self.clear_button = QPushButton("清空数据库")
        self.clear_button.setIcon(QIcon.fromTheme("edit-clear", QIcon(get_resource_path("clear.png"))))
        self.clear_button.setMinimumHeight(35)
        self.clear_button.clicked.connect(self.clearDatabase)
        button_layout.addWidget(self.clear_button)

        self.export_button = QPushButton("导出选中")
        self.export_button.setIcon(QIcon.fromTheme("document-export", QIcon(get_resource_path("export.png"))))
        self.export_button.setMinimumHeight(35)
        self.export_button.clicked.connect(self.exportSelectedRecords)
        button_layout.addWidget(self.export_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # 使用分割器分割记录列表和详细信息
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(8)
        layout.addWidget(splitter)

        # 记录列表
        records_widget = QWidget()
        records_layout = QVBoxLayout(records_widget)
        records_layout.setContentsMargins(0, 0, 0, 0)

        records_title = QLabel("解析记录列表")
        records_title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        records_layout.addWidget(records_title)

        self.records_table = QTableWidget()
        self.records_table.setColumnCount(5)
        self.records_table.setHorizontalHeaderLabels(["ID", "文件名", "解析时间", "数据段数", "总行数"])
        self.records_table.horizontalHeader().setStretchLastSection(True)
        self.records_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.records_table.setAlternatingRowColors(True)
        self.records_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #0078d4;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        records_layout.addWidget(self.records_table)
        splitter.addWidget(records_widget)

        # 详细信息标签页
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(0, 0, 0, 0)

        detail_title = QLabel("记录详细信息")
        detail_title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        detail_layout.addWidget(detail_title)

        self.detail_tab_widget = QTabWidget()
        self.detail_tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: #333;
                padding: 8px 16px;
                border: 1px solid #d0d0d0;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        detail_layout.addWidget(self.detail_tab_widget)

        # 文件概览标签页
        self.summary_tab = QWidget()
        self.initSummaryTab()
        self.detail_tab_widget.addTab(self.summary_tab, "文件概览")

        # 详细数据标签页
        self.data_tab = QWidget()
        self.initDataTab()
        self.detail_tab_widget.addTab(self.data_tab, "详细数据")

        splitter.addWidget(detail_widget)

        # 设置分割器比例
        splitter.setSizes([300, 400])

        # 初始化当前结果
        self.current_db_result = None

        # 加载数据
        self.loadDatabaseRecords()

    def initSummaryTab(self):
        """初始化文件概览标签页"""
        layout = QVBoxLayout(self.summary_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        info_group = QGroupBox("文件信息")
        info_group.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(15, 15, 15, 15)

        self.db_info_table = QTableWidget()
        self.db_info_table.setColumnCount(2)
        self.db_info_table.setHorizontalHeaderLabels(["参数", "值"])
        self.db_info_table.horizontalHeader().setStretchLastSection(True)
        self.db_info_table.setAlternatingRowColors(True)
        self.db_info_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
        """)
        info_layout.addWidget(self.db_info_table)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        stats_group = QGroupBox("统计信息")
        stats_group.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(15, 15, 15, 15)

        self.db_stats_table = QTableWidget()
        self.db_stats_table.setColumnCount(2)
        self.db_stats_table.setHorizontalHeaderLabels(["统计项", "值"])
        self.db_stats_table.horizontalHeader().setStretchLastSection(True)
        self.db_stats_table.setAlternatingRowColors(True)
        self.db_stats_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
        """)
        stats_layout.addWidget(self.db_stats_table)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        layout.addStretch()

    def initDataTab(self):
        """初始化详细数据标签页"""
        layout = QVBoxLayout(self.data_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        self.db_section_table = QTableWidget()
        self.db_section_table.setColumnCount(4)
        self.db_section_table.setHorizontalHeaderLabels(["类型", "标签", "日期", "时间"])
        self.db_section_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.db_section_table.setMaximumHeight(150)
        self.db_section_table.setAlternatingRowColors(True)
        self.db_section_table.cellClicked.connect(self.onDBSectionClicked)
        self.db_section_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.db_section_table)

        self.db_data_table = QTableWidget()
        self.db_data_table.horizontalHeader().setStretchLastSection(True)
        self.db_data_table.setAlternatingRowColors(True)
        self.db_data_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.db_data_table)

    def loadDatabaseRecords(self):
        """加载数据库记录到表格"""
        try:
            rows = query_results()
            self.records_table.setRowCount(len(rows))

            for row_idx, row in enumerate(rows):
                id_item = QTableWidgetItem(str(row[0]))
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                id_item.setTextAlignment(Qt.AlignCenter)
                self.records_table.setItem(row_idx, 0, id_item)

                filename_item = QTableWidgetItem(row[1])
                filename_item.setFlags(filename_item.flags() & ~Qt.ItemIsEditable)
                self.records_table.setItem(row_idx, 1, filename_item)

                time_item = QTableWidgetItem(row[2])
                time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)
                time_item.setTextAlignment(Qt.AlignCenter)
                self.records_table.setItem(row_idx, 2, time_item)

                # 解析JSON获取统计信息
                summary_json = row[3]
                try:
                    summary = json.loads(summary_json)
                    sections_count = len(summary.get("sections", []))
                    total_rows = sum(sum(t["row_count"] for t in s["tables"]) for s in summary.get("sections", []))
                except:
                    sections_count = 0
                    total_rows = 0

                sections_item = QTableWidgetItem(str(sections_count))
                sections_item.setFlags(sections_item.flags() & ~Qt.ItemIsEditable)
                sections_item.setTextAlignment(Qt.AlignCenter)
                self.records_table.setItem(row_idx, 3, sections_item)

                rows_item = QTableWidgetItem(str(total_rows))
                rows_item.setFlags(rows_item.flags() & ~Qt.ItemIsEditable)
                rows_item.setTextAlignment(Qt.AlignCenter)
                self.records_table.setItem(row_idx, 4, rows_item)

            # 连接选择变化事件
            self.records_table.itemSelectionChanged.connect(self.onRecordSelected)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据库记录失败: {str(e)}")

    def onRecordSelected(self):
        """选中记录时显示详细信息"""
        selected_items = self.records_table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()

        try:
            # 重新查询数据库获取完整记录
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT summary_json FROM parse_results WHERE id = ?", (self.records_table.item(row, 0).text(),))
            result = cur.fetchone()
            conn.close()

            if result:
                summary = json.loads(result[0])
                self.current_db_result = summary
                self.displayDBSummary(summary)
                self.displayDBDataSections(summary)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"显示详细信息失败: {str(e)}")

    def displayDBSummary(self, result):
        """显示数据库记录的文件概览信息"""
        self.db_info_table.setRowCount(0)
        self.db_info_table.setRowCount(6)

        self.db_info_table.setItem(0, 0, QTableWidgetItem("文件名"))
        self.db_info_table.setItem(0, 1, QTableWidgetItem(os.path.basename(result["filename"])))

        self.db_info_table.setItem(1, 0, QTableWidgetItem("解析时间"))
        self.db_info_table.setItem(1, 1, QTableWidgetItem(result["parse_time"]))

        self.db_info_table.setItem(2, 0, QTableWidgetItem("System"))
        self.db_info_table.setItem(2, 1, QTableWidgetItem(result["header"].get("System", "N/A")))

        self.db_info_table.setItem(3, 0, QTableWidgetItem("Version"))
        self.db_info_table.setItem(3, 1, QTableWidgetItem(result["header"].get("Version", "N/A")))

        self.db_info_table.setItem(4, 0, QTableWidgetItem("Code"))
        self.db_info_table.setItem(4, 1, QTableWidgetItem(result["header"].get("Code", "N/A")))

        self.db_info_table.setItem(5, 0, QTableWidgetItem("Data"))
        self.db_info_table.setItem(5, 1, QTableWidgetItem(result["header"].get("Data", "N/A")))

        total_sections = len(result["sections"])
        total_tables = sum(len(s["tables"]) for s in result["sections"])
        total_rows = sum(sum(t["row_count"] for t in s["tables"]) for s in result["sections"])

        self.db_stats_table.setRowCount(0)
        self.db_stats_table.setRowCount(3)

        self.db_stats_table.setItem(0, 0, QTableWidgetItem("数据段数量"))
        self.db_stats_table.setItem(0, 1, QTableWidgetItem(str(total_sections)))

        self.db_stats_table.setItem(1, 0, QTableWidgetItem("数据表数量"))
        self.db_stats_table.setItem(1, 1, QTableWidgetItem(str(total_tables)))

        self.db_stats_table.setItem(2, 0, QTableWidgetItem("总数据行数"))
        self.db_stats_table.setItem(2, 1, QTableWidgetItem(str(total_rows)))

    def displayDBDataSections(self, result):
        """显示数据库记录的数据段信息"""
        self.db_section_table.setRowCount(0)
        self.db_section_table.setRowCount(len(result["sections"]))

        for idx, section in enumerate(result["sections"]):
            self.db_section_table.setItem(idx, 0, QTableWidgetItem(section["type"]))
            self.db_section_table.setItem(idx, 1, QTableWidgetItem(section["tag"]))
            self.db_section_table.setItem(idx, 2, QTableWidgetItem(section["date"]))
            self.db_section_table.setItem(idx, 3, QTableWidgetItem(section["time"]))

        if len(result["sections"]) > 0:
            self.db_section_table.selectRow(0)
            self.onDBSectionClicked(0, 0)

    def onDBSectionClicked(self, row, column):
        """处理数据库记录数据段点击"""
        if self.current_db_result is None or row >= len(self.current_db_result["sections"]):
            return

        section = self.current_db_result["sections"][row]

        if len(section["tables"]) == 0:
            self.db_data_table.setRowCount(0)
            self.db_data_table.setColumnCount(0)
            return

        table = section["tables"][0]
        header_count = len(table["header"])
        row_count = len(table["rows"])

        self.db_data_table.setColumnCount(header_count)
        self.db_data_table.setHorizontalHeaderLabels(table["header"])

        # 对于数据库记录，限制显示行数以提高性能
        max_display_rows = min(row_count, 100)

        self.db_data_table.setRowCount(max_display_rows)

        for row_idx in range(max_display_rows):
            row_data = table["rows"][row_idx]
            for col_idx, header in enumerate(table["header"]):
                value = row_data.get(header, "")
                self.db_data_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def formatRecordDetail(self, summary):
        """格式化记录详细信息"""
        detail = f"文件名: {summary.get('filename', 'N/A')}\n"
        detail += f"解析时间: {summary.get('parse_time', 'N/A')}\n\n"

        detail += "系统信息:\n"
        for key, value in summary.get("header", {}).items():
            detail += f"  {key}: {value}\n"
        detail += "\n"

        detail += "数据段信息:\n"
        for idx, section in enumerate(summary.get("sections", []), 1):
            detail += f"  [{idx}] {section['type']} - {section['tag']}\n"
            detail += f"      场站: {section['station']}\n"
            detail += f"      日期: {section['date']}\n"
            detail += f"      时间: {section['time']}\n"
            detail += f"      数据表数量: {len(section['tables'])}\n"
            detail += f"      总行数: {sum(t['row_count'] for t in section['tables'])}\n\n"

        return detail

    def deleteSelectedRecords(self):
        """删除选中的记录"""
        selected_items = self.records_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要删除的记录")
            return

        row = selected_items[0].row()
        record_id = self.records_table.item(row, 0).text()

        reply = QMessageBox.question(self, "确认删除", "确定要删除选中的记录吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("DELETE FROM parse_results WHERE id = ?", (record_id,))
                conn.commit()
                conn.close()

                QMessageBox.information(self, "成功", "记录已删除")
                self.loadDatabaseRecords()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除记录失败: {str(e)}")

    def clearDatabase(self):
        """清空数据库"""
        reply = QMessageBox.question(self, "确认清空", "确定要清空整个数据库吗？此操作不可恢复！",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("DELETE FROM parse_results")
                conn.commit()
                conn.close()

                QMessageBox.information(self, "成功", "数据库已清空")
                self.loadDatabaseRecords()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"清空数据库失败: {str(e)}")

    def exportSelectedRecords(self):
        """导出选中的记录"""
        selected_items = self.records_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要导出的记录")
            return

        row = selected_items[0].row()
        record_id = self.records_table.item(row, 0).text()

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT summary_json FROM parse_results WHERE id = ?", (record_id,))
            result = cur.fetchone()
            conn.close()

            if result:
                summary = json.loads(result[0])
                filepath, _ = QFileDialog.getSaveFileName(self, "保存记录", "", "文本文件 (*.txt);;所有文件 (*.*)")

                if filepath:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write("=" * 60 + "\n")
                        f.write("数据库记录导出\n")
                        f.write("=" * 60 + "\n\n")

                        f.write("文件信息:\n")
                        f.write("  文件名: " + summary.get("filename", "N/A") + "\n")
                        f.write("  解析时间: " + summary.get("parse_time", "N/A") + "\n\n")

                        f.write("系统信息:\n")
                        for key, value in summary.get("header", {}).items():
                            f.write("  " + key + ": " + str(value) + "\n")
                        f.write("\n")

                        f.write("统计信息:\n")
                        total_sections = len(summary.get("sections", []))
                        total_tables = sum(len(s["tables"]) for s in summary.get("sections", []))
                        total_rows = sum(sum(t["row_count"] for t in s["tables"]) for s in summary.get("sections", []))
                        f.write("  数据段数量: " + str(total_sections) + "\n")
                        f.write("  数据表数量: " + str(total_tables) + "\n")
                        f.write("  总数据行数: " + str(total_rows) + "\n\n")

                        for idx, section in enumerate(summary.get("sections", []), 1):
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
                        f.write("国家电投云南国际昆明生产运营中心 版权所有\n")
                        f.write("版本: 2.2.0\n")
                        f.write("作者：陈丰 电话：0871-65666603\n")
                        f.write("记录导出完成\n")
                        f.write("=" * 60 + "\n")

                    QMessageBox.information(self, "成功", "记录已导出")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出记录失败: {str(e)}")

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
            # 保存到数据库
            save_result(result)
            self.finished.emit(result, self.filepath)
            self.progress.emit(100)
        except Exception as e:
            self.error.emit(str(e))

# --------------- Excel风格的表格代理 ---------------
class ExcelStyleDelegate(QItemDelegate):
    """Excel风格的单元格代理，提供更好的编辑体验"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def createEditor(self, parent, option, index):
        """创建编辑器"""
        editor = QLineEdit(parent)
        editor.setFrame(False)
        editor.setStyleSheet("""
            QLineEdit {
                border: 1px solid #0078d4;
                background-color: white;
                padding: 2px;
            }
        """)
        return editor
    
    def setEditorData(self, editor, index):
        """设置编辑器数据"""
        value = index.model().data(index, Qt.DisplayRole)
        editor.setText(str(value) if value is not None else "")
    
    def setModelData(self, editor, model, index):
        """设置模型数据"""
        value = editor.text()
        model.setData(index, value, Qt.EditRole)

# --------------- Excel风格的状态栏 ---------------
class ExcelStatusBar(QStatusBar):
    """Excel风格的状态栏，显示更多统计信息"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # 当前单元格位置显示
        self.cell_position = QLabel("A1")
        self.cell_position.setStyleSheet("font-weight: bold; color: #0078d4;")
        self.addWidget(self.cell_position)
        
        # 分隔符
        self.addPermanentWidget(QLabel(" | "))
        
        # 选中单元格数量
        self.selection_count = QLabel("选中: 0")
        self.addWidget(self.selection_count)
        
        # 分隔符
        self.addPermanentWidget(QLabel(" | "))
        
        # 数据统计
        self.data_stats = QLabel("行: 0, 列: 0")
        self.addWidget(self.data_stats)
        
        # 分隔符
        self.addPermanentWidget(QLabel(" | "))
        
        # 版权信息
        self.copyright_label = QLabel("国家电投云南国际昆明生产运营中心 版权所有 | Ver: 2.2.0 | 联系电话: 0871-65666603")
        self.addWidget(self.copyright_label)
        
    def updateCellPosition(self, row, col):
        """更新当前单元格位置"""
        # Excel风格的列字母表示
        col_letter = self._get_column_letter(col + 1)
        self.cell_position.setText(f"{col_letter}{row + 1}")
        
    def updateSelectionCount(self, count):
        """更新选中单元格数量"""
        self.selection_count.setText(f"选中: {count}")
        
    def updateDataStats(self, rows, cols):
        """更新数据统计"""
        self.data_stats.setText(f"行: {rows}, 列: {cols}")
        
    def _get_column_letter(self, col_num):
        """将列号转换为Excel风格的字母表示"""
        result = ""
        while col_num > 0:
            col_num, remainder = divmod(col_num - 1, 26)
            result = chr(65 + remainder) + result
        return result

# --------------- Excel风格的表格视图 ---------------
class ExcelTableView(QTableWidget):
    """Excel风格的数据表格视图"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # 设置Excel风格的样式
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setShowGrid(True)
        self.setGridStyle(Qt.SolidLine)
        
        # 设置表头样式
        header = self.horizontalHeader()
        header.setSectionsMovable(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setDefaultSectionSize(100)
        
        # 设置垂直表头（行号）
        vheader = self.verticalHeader()
        vheader.setDefaultSectionSize(25)
        vheader.setSectionResizeMode(QHeaderView.Fixed)
        
        # 设置代理
        self.setItemDelegate(ExcelStyleDelegate(self))
        
        # 连接信号
        self.cellChanged.connect(self.onCellChanged)
        self.currentCellChanged.connect(self.onCurrentCellChanged)
        
    def onCellChanged(self, row, col):
        """单元格内容改变时的处理"""
        pass  # 可以在这里添加数据验证等逻辑
        
    def onCurrentCellChanged(self, currentRow, currentCol, previousRow, previousCol):
        """当前单元格改变时的处理"""
        if hasattr(self.parent(), 'statusBar') and hasattr(self.parent().statusBar, 'updateCellPosition'):
            self.parent().statusBar.updateCellPosition(currentRow, currentCol)
            
    def keyPressEvent(self, event):
        """键盘事件处理，支持Excel风格的快捷键"""
        if event.key() == Qt.Key_F2:
            # F2编辑模式
            current_item = self.currentItem()
            if current_item:
                self.editItem(current_item)
        elif event.key() == Qt.Key_Delete:
            # Delete删除内容
            selected_items = self.selectedItems()
            for item in selected_items:
                item.setText("")
        else:
            super().keyPressEvent(event)

# --------------- Excel风格的工具栏 ---------------
class ExcelToolBar(QToolBar):
    """Excel风格的工具栏"""
    def __init__(self, parent=None):
        super().__init__("Excel工具栏", parent)
        self.initUI()
        
    def initUI(self):
        # 文件操作
        self.addAction(QIcon.fromTheme("document-open"), "打开", self.parent().browseFile)
        self.addAction(QIcon.fromTheme("document-save"), "保存", self.parent().exportReport)
        self.addSeparator()
        
        # 编辑操作
        self.addAction(QIcon.fromTheme("edit-copy"), "复制", self.copySelection)
        self.addAction(QIcon.fromTheme("edit-paste"), "粘贴", self.pasteSelection)
        self.addAction(QIcon.fromTheme("edit-cut"), "剪切", self.cutSelection)
        self.addSeparator()
        
        # 视图操作
        self.addAction(QIcon.fromTheme("zoom-in"), "放大", self.zoomIn)
        self.addAction(QIcon.fromTheme("zoom-out"), "缩小", self.zoomOut)
        self.addAction(QIcon.fromTheme("view-refresh"), "刷新", self.refreshView)
        
    def copySelection(self):
        """复制选中的单元格"""
        table = self.parent().data_table
        selected_items = table.selectedItems()
        if not selected_items:
            return
            
        # 按行和列组织数据
        rows = {}
        for item in selected_items:
            row, col = item.row(), item.column()
            if row not in rows:
                rows[row] = {}
            rows[row][col] = item.text()
            
        # 转换为制表符分隔的文本
        if rows:
            text = ""
            for row in sorted(rows.keys()):
                row_data = []
                for col in sorted(rows[row].keys()):
                    row_data.append(rows[row][col])
                text += "\t".join(row_data) + "\n"
                
            # 复制到剪贴板
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
    def pasteSelection(self):
        """粘贴到选中的单元格"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if not text:
            return
            
        table = self.parent().data_table
        current_item = table.currentItem()
        if not current_item:
            return
            
        # 解析剪贴板数据
        lines = text.strip().split('\n')
        start_row = current_item.row()
        start_col = current_item.column()
        
        for row_offset, line in enumerate(lines):
            cells = line.split('\t')
            for col_offset, cell_text in enumerate(cells):
                row = start_row + row_offset
                col = start_col + col_offset
                
                # 确保表格有足够的行列
                while table.rowCount() <= row:
                    table.insertRow(table.rowCount())
                while table.columnCount() <= col:
                    table.insertColumn(table.columnCount())
                    
                # 设置单元格内容
                item = table.item(row, col)
                if not item:
                    item = QTableWidgetItem()
                    table.setItem(row, col, item)
                item.setText(cell_text)
                
    def cutSelection(self):
        """剪切选中的单元格"""
        self.copySelection()
        table = self.parent().data_table
        selected_items = table.selectedItems()
        for item in selected_items:
            item.setText("")
            
    def zoomIn(self):
        """放大视图"""
        table = self.parent().data_table
        font = table.font()
        font.setPointSize(font.pointSize() + 1)
        table.setFont(font)
        
    def zoomOut(self):
        """缩小视图"""
        table = self.parent().data_table
        font = table.font()
        font.setPointSize(max(8, font.pointSize() - 1))
        table.setFont(font)
        
    def refreshView(self):
        """刷新视图"""
        if hasattr(self.parent(), 'current_result') and self.parent().current_result:
            self.parent().displayDataSections(self.parent().current_result)

# --------------- 主界面 ---------------
class EFileViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_result = None
        self.current_theme = "light"
        self.is_maximized = False

        self.initUI()
        self.apply_theme()

    def initUI(self):
        self.setWindowTitle("南网102-e文件解析工具 v2.2.0")
        self.setGeometry(100, 100, 1024, 768)
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon(get_resource_path("spic_logo.png")))
        
        # 设置窗口样式为自定义
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # Header（Logo + 标题）
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(15)

        self.logo_label = QLabel()
        logo_pixmap = self.load_logo()
        if logo_pixmap:
            self.logo_label.setPixmap(logo_pixmap)
        else:
            self.logo_label.setText("SPIC")
            self.logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #E60012;")
        header_layout.addWidget(self.logo_label)

        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        self.main_title = QLabel("国家电投云南国际昆明生产运营中心")
        self.main_title.setAlignment(Qt.AlignLeft)
        self.main_title.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_layout.addWidget(self.main_title)

        self.subtitle = QLabel("南网102-e文件解析工具 v2.2.0")
        self.subtitle.setAlignment(Qt.AlignLeft)
        self.subtitle.setFont(QFont("Microsoft YaHei", 12))
        self.subtitle.setStyleSheet("color: #666;")
        title_layout.addWidget(self.subtitle)

        self.description = QLabel("根据《南方电网新能源数据上送规范V3.3修订版》解析e文件")
        self.description.setAlignment(Qt.AlignLeft)
        self.description.setFont(QFont("Microsoft YaHei", 9))
        self.description.setStyleSheet("color: #888;")
        title_layout.addWidget(self.description)

        header_layout.addWidget(title_widget)
        header_layout.addStretch()

        self.main_layout.addWidget(header_widget)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(line)

        # Buttons Row
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet(
            "padding: 10px; background: #f0f0f0; color: #333; border-radius: 5px; border: 1px solid #d0d0d0;"
        )
        self.file_label.setMinimumWidth(300)
        self.file_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(self.file_label)

        self.browse_button = QPushButton("选择文件")
        self.browse_button.setIcon(QIcon.fromTheme("document-open", QIcon(get_resource_path("folder.png"))))
        self.browse_button.setMinimumWidth(100)
        self.browse_button.setMinimumHeight(35)
        self.browse_button.clicked.connect(self.browseFile)
        button_layout.addWidget(self.browse_button)

        self.parse_button = QPushButton("解析")
        self.parse_button.setIcon(QIcon.fromTheme("system-run", QIcon(get_resource_path("parse.png"))))
        self.parse_button.setMinimumWidth(100)
        self.parse_button.setMinimumHeight(35)
        self.parse_button.setEnabled(False)
        self.parse_button.clicked.connect(self.parseFile)
        button_layout.addWidget(self.parse_button)

        # 添加数据库管理按钮到按钮行
        self.db_manage_button = QPushButton("数据库管理")
        self.db_manage_button.setIcon(QIcon.fromTheme("view-list", QIcon(get_resource_path("database.png"))))
        self.db_manage_button.setMinimumWidth(100)
        self.db_manage_button.setMinimumHeight(35)
        self.db_manage_button.clicked.connect(self.openDatabaseManager)
        button_layout.addWidget(self.db_manage_button)

        self.export_button = QPushButton("导出报告")
        self.export_button.setIcon(QIcon.fromTheme("document-save", QIcon(get_resource_path("export.png"))))
        self.export_button.setMinimumWidth(100)
        self.export_button.setMinimumHeight(35)
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.exportReport)
        button_layout.addWidget(self.export_button)

        button_layout.addStretch()

        self.limit_checkbox = QCheckBox("限制显示(提高性能)")
        self.limit_checkbox.setChecked(True)
        button_layout.addWidget(self.limit_checkbox)

        self.main_layout.addWidget(button_widget)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #d0d0d0;
                border-radius: 5px;
                text-align: center;
                background-color: #fff;
                color: #000;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        self.main_layout.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            padding: 10px;
            background: #f9f9f9;
            border-radius: 5px;
            border: 1px solid #d0d0d0;
            font-size: 14px;
        """)
        self.main_layout.addWidget(self.status_label)

        # Excel风格的工具栏
        self.excel_toolbar = ExcelToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.excel_toolbar)
        
        # Tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #d0d0d0;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: #333;
                padding: 10px 20px;
                border: 1px solid #d0d0d0;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
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

        # Excel风格的状态栏
        self.statusBar = ExcelStatusBar(self)
        self.setStatusBar(self.statusBar)

        self.thread = None

        # Theme check timer
        self.theme_timer = QTimer()
        self.theme_timer.timeout.connect(self.check_theme_change)
        self.theme_timer.start(5000)

    def load_logo(self):
        """加载LOGO图片"""
        try:
            logo_path = get_resource_path("spic_logo.png")
            if os.path.exists(logo_path):
                logo_pixmap = QPixmap(logo_path)
                if not logo_pixmap.isNull():
                    return logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        except Exception:
            pass
        return None

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
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        info_group = QGroupBox("文件信息")
        info_group.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(15, 15, 15, 15)

        self.info_table = QTableWidget()
        self.info_table.setColumnCount(2)
        self.info_table.setHorizontalHeaderLabels(["参数", "值"])
        self.info_table.horizontalHeader().setStretchLastSection(True)
        self.info_table.setAlternatingRowColors(True)
        self.info_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
        """)
        info_layout.addWidget(self.info_table)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        stats_group = QGroupBox("统计信息")
        stats_group.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(15, 15, 15, 15)

        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["统计项", "值"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
        """)
        stats_layout.addWidget(self.stats_table)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        layout.addStretch()

    # -------------- Tab: Data --------------
    def initDataTab(self):
        layout = QVBoxLayout(self.data_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        self.section_table = QTableWidget()
        self.section_table.setColumnCount(4)
        self.section_table.setHorizontalHeaderLabels(["类型", "标签", "日期", "时间"])
        self.section_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.section_table.setMaximumHeight(150)
        self.section_table.setAlternatingRowColors(True)
        self.section_table.cellClicked.connect(self.onSectionClicked)
        self.section_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.section_table)

        self.data_table = ExcelTableView(self)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.data_table)

    # -------------- Tab: Raw --------------
    def initRawTab(self):
        layout = QVBoxLayout(self.raw_tab)
        layout.setContentsMargins(15, 15, 15, 15)

        self.raw_text = QTextEdit()
        self.raw_text.setReadOnly(True)
        self.raw_text.setFont(QFont("Consolas", 9))
        self.raw_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.raw_text)

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

        # lbx 的解压内容预览
        if "lbx_info" in result and result["lbx_info"]:
            lbx_info = result["lbx_info"]
            lbx_name = lbx_info.get("lbx_name", "")
            dat_count = lbx_info.get("dat_count", 0)

            content = "= lbx 文件信息 =\n"
            content += f"文件名: {lbx_name}\n"
            content += f"包含 .dat 文件数: {dat_count}\n\n"
            content += "= 数据段信息 =\n"
            content += f"总数据段数: {len(result['sections'])}\n\n"
            content += "= 解压内容预览 =\n"
            content += "(LBX文件已解压，数据段信息见上)\n"

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
                    f.write("版本: 2.2.0\n")
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
                    f.write("国家电投云南国际昆明生产运营中心 版权所有\n")
                    f.write("版本: 2.2.0\n")
                    f.write("作者：陈丰 电话：0871-65666603\n")
                    f.write("报告生成完成\n")
                    f.write("=" * 60 + "\n")

                QMessageBox.information(self, "成功", "报告已成功导出！")
            except Exception as e:
                QMessageBox.critical(self, "错误", "导出失败:\n" + str(e))

    # -------------- 文件浏览 --------------
    def browseFile(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "选择E文件", "", "E文件 (*.tar.gz);;E文件 (*.dat);;E文件 (*.lbx);;所有文件 (*.*)")
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
        self.status_label.setStyleSheet("""
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
            border: 1px solid #d0d0d0;
        """)

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
        self.status_label.setStyleSheet("""
            padding: 10px;
            background: #ffebee;
            border-radius: 5px;
            border: 1px solid #ef9a9a;
            color: #d32f2f;
        """)
        QMessageBox.critical(self, "解析错误", "解析E文件时出错:\n" + error_msg)
        self.parse_button.setEnabled(True)
        self.browse_button.setEnabled(True)

    # -------------- 解析完成 --------------
    def onParseFinished(self, result, filepath):
        try:
            self.current_result = result
            self.progress_bar.setVisible(False)
            self.status_label.setText("解析完成！")
            self.status_label.setStyleSheet("""
                padding: 10px;
                background: #e8f5e9;
                border-radius: 5px;
                border: 1px solid #a5d6a7;
                color: #2e7d32;
            """)

            self.displaySummary(result)
            self.displayDataSections(result)
            self.displayRaw(result)

            self.parse_button.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.export_button.setEnabled(True)
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_label.setText("显示数据时出错: " + str(e))
            self.status_label.setStyleSheet("""
                padding: 10px;
                background: #ffebee;
                border-radius: 5px;
                border: 1px solid #ef9a9a;
                color: #d32f2f;
            """)
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

    # -------------- 数据库管理 --------------
    def openDatabaseManager(self):
        """打开数据库管理对话框"""
        dialog = DatabaseManagerDialog(self)
        dialog.exec()

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
        QHeaderView::section { background-color: #0078d4; color: white; padding: 8px; border: 1px solid #005a9e; }
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
        QHeaderView::section { background-color: #0078d4; color: white; padding: 8px; border: 1px solid #005a9e; }
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
