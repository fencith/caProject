# -*- coding: utf-8 -*-
"""
E文件解析工具 - PySide6 版本 v2.1.3 优化版
国家电投云南国际  昆明生产运营中心 版权所有
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
from typing import Dict, List, Any, Optional, Tuple, Generator
from contextlib import contextmanager

# Lite 版本及 PDF 功能清理已移除

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QTableWidget, QTableWidgetItem, QTabWidget,
    QTextEdit, QMessageBox, QProgressBar,
    QGroupBox, QStatusBar, QCheckBox, QComboBox, QDialog, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon

from efile_parser import parse_efile
from db_utils import init_db, save_result, query_results

# --------------- 常量定义 ----------------
class Constants:
    """应用常量定义"""
    MAX_DISPLAY_ROWS = 1000
    MAX_RAW_CONTENT_LENGTH = 100000
    MAX_PREVIEW_ROWS = 100
    THEME_CHECK_INTERVAL = 5000  # 5秒
    APP_VERSION = "2.1.3"
    WINDOW_TITLE = "南网102-e文件解析工具"
    WINDOW_SIZE = (1024, 768)
    LOGO_SIZE = (80, 80)
    BUTTON_MIN_WIDTH = 100
    TABLE_MAX_HEIGHT = 150
    PROGRESS_STEPS = [30, 70, 100]
    ENCODINGS = ["utf-8", "gbk", "gb2312", "gb18030", "utf-16"]

# --------------- 工具函数 ----------------
@contextmanager
def database_connection(db_path: str):
    """数据库连接上下文管理器"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def safe_get(data: Dict[str, Any], key: str, default: Any = "N/A") -> Any:
    """安全获取字典值"""
    return data.get(key, default)

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

# --------------- 数据库管理对话框 ----------------
class DatabaseManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("数据库管理")
        self.setGeometry(200, 200, 1000, 700)
        # 添加窗口标志，启用最大化和最小化按钮
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # 按钮行
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("刷新列表")
        self.refresh_button.clicked.connect(self.loadDatabaseRecords)
        button_layout.addWidget(self.refresh_button)

        self.delete_button = QPushButton("删除选中")
        self.delete_button.clicked.connect(self.deleteSelectedRecords)
        button_layout.addWidget(self.delete_button)

        self.clear_button = QPushButton("清空数据库")
        self.clear_button.clicked.connect(self.clearDatabase)
        button_layout.addWidget(self.clear_button)

        self.export_button = QPushButton("导出选中")
        self.export_button.clicked.connect(self.exportSelectedRecords)
        button_layout.addWidget(self.export_button)

        layout.addLayout(button_layout)

        # 使用分割器分割记录列表和详细信息
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)

        # 记录列表
        records_widget = QWidget()
        records_layout = QVBoxLayout(records_widget)
        records_layout.addWidget(QLabel("解析记录列表"))
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(5)
        self.records_table.setHorizontalHeaderLabels(["ID", "文件名", "解析时间", "数据段数", "总行数"])
        self.records_table.horizontalHeader().setStretchLastSection(True)
        self.records_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        records_layout.addWidget(self.records_table)
        splitter.addWidget(records_widget)

        # 详细信息标签页
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.addWidget(QLabel("记录详细信息"))

        self.detail_tab_widget = QTabWidget()
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

        info_group = QGroupBox("文件信息")
        info_layout = QVBoxLayout()
        self.db_info_table = QTableWidget()
        self.db_info_table.setColumnCount(2)
        self.db_info_table.setHorizontalHeaderLabels(["参数", "值"])
        self.db_info_table.horizontalHeader().setStretchLastSection(True)
        info_layout.addWidget(self.db_info_table)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        stats_group = QGroupBox("统计信息")
        stats_layout = QVBoxLayout()
        self.db_stats_table = QTableWidget()
        self.db_stats_table.setColumnCount(2)
        self.db_stats_table.setHorizontalHeaderLabels(["统计项", "值"])
        self.db_stats_table.horizontalHeader().setStretchLastSection(True)
        stats_layout.addWidget(self.db_stats_table)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

    def initDataTab(self):
        """初始化详细数据标签页"""
        layout = QVBoxLayout(self.data_tab)

        self.db_section_table = QTableWidget()
        self.db_section_table.setColumnCount(4)
        self.db_section_table.setHorizontalHeaderLabels(["类型", "标签", "日期", "时间"])
        self.db_section_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.db_section_table.setMaximumHeight(Constants.TABLE_MAX_HEIGHT)
        self.db_section_table.cellClicked.connect(self.onDBSectionClicked)
        layout.addWidget(self.db_section_table)

        self.db_data_table = QTableWidget()
        self.db_data_table.horizontalHeader().setStretchLastSection(True)
        self.db_data_table.setAlternatingRowColors(True)
        layout.addWidget(self.db_data_table)

    def loadDatabaseRecords(self):
        """加载数据库记录到表格"""
        try:
            # 首先检查数据库是否存在
            if not os.path.exists(DB_PATH):
                QMessageBox.information(self, "提示", "数据库文件不存在，将创建新的数据库。")
                init_db()

            rows = query_results()
            self.records_table.setRowCount(len(rows))

            for row_idx, row in enumerate(rows):
                id_item = QTableWidgetItem(str(row[0]))
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                self.records_table.setItem(row_idx, 0, id_item)

                filename_item = QTableWidgetItem(row[1])
                filename_item.setFlags(filename_item.flags() & ~Qt.ItemIsEditable)
                self.records_table.setItem(row_idx, 1, filename_item)

                time_item = QTableWidgetItem(row[2])
                time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)
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
                self.records_table.setItem(row_idx, 3, sections_item)

                rows_item = QTableWidgetItem(str(total_rows))
                rows_item.setFlags(rows_item.flags() & ~Qt.ItemIsEditable)
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
            with database_connection(DB_PATH) as conn:
                cur = conn.cursor()
                record_id = self.records_table.item(row, 0).text()
                cur.execute("SELECT summary_json FROM parse_results WHERE id = ?", (record_id,))
                result = cur.fetchone()

            if result and result[0]:
                summary = json.loads(result[0])
                self.current_db_result = summary
                self.displayDBSummary(summary)
                self.displayDBDataSections(summary)
            else:
                QMessageBox.warning(self, "警告", "选中的记录数据为空")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "错误", f"解析记录数据失败: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"显示详细信息失败: {str(e)}")

    def displayDBSummary(self, result: Dict[str, Any]):
        """显示数据库记录的文件概览信息"""
        self.db_info_table.setRowCount(0)
        self.db_info_table.setRowCount(6)

        self.db_info_table.setItem(0, 0, QTableWidgetItem("文件名"))
        self.db_info_table.setItem(0, 1, QTableWidgetItem(os.path.basename(result["filename"])))

        self.db_info_table.setItem(1, 0, QTableWidgetItem("解析时间"))
        self.db_info_table.setItem(1, 1, QTableWidgetItem(result["parse_time"]))

        self.db_info_table.setItem(2, 0, QTableWidgetItem("System"))
        self.db_info_table.setItem(2, 1, QTableWidgetItem(safe_get(result["header"], "System")))

        self.db_info_table.setItem(3, 0, QTableWidgetItem("Version"))
        self.db_info_table.setItem(3, 1, QTableWidgetItem(safe_get(result["header"], "Version")))

        self.db_info_table.setItem(4, 0, QTableWidgetItem("Code"))
        self.db_info_table.setItem(4, 1, QTableWidgetItem(safe_get(result["header"], "Code")))

        self.db_info_table.setItem(5, 0, QTableWidgetItem("Data"))
        self.db_info_table.setItem(5, 1, QTableWidgetItem(safe_get(result["header"], "Data")))

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

    def displayDBDataSections(self, result: Dict[str, Any]):
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

    def onDBSectionClicked(self, row: int, column: int):
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
        max_display_rows = min(row_count, Constants.MAX_DISPLAY_ROWS)

        self.db_data_table.setRowCount(max_display_rows)

        for row_idx in range(max_display_rows):
            row_data = table["rows"][row_idx]
            for col_idx, header in enumerate(table["header"]):
                value = row_data.get(header, "")
                self.db_data_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def formatRecordDetail(self, summary: Dict[str, Any]) -> str:
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
                with database_connection(DB_PATH) as conn:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM parse_results WHERE id = ?", (record_id,))
                    conn.commit()

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
                with database_connection(DB_PATH) as conn:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM parse_results")
                    conn.commit()

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
            with database_connection(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("SELECT summary_json FROM parse_results WHERE id = ?", (record_id,))
                result = cur.fetchone()

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
                        f.write("国家电投云南国际  昆明生产运营中心 版权所有\n")
                        f.write("版本: 2.1.3\n")
                        f.write("作者：陈丰 电话：0871-65666603\n")
                        f.write("记录导出完成\n")
                        f.write("=" * 60 + "\n")

                    QMessageBox.information(self, "成功", "记录已导出")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出记录失败: {str(e)}")

# 获取exe所在目录的路径（适用于打包后的exe）
if getattr(sys, 'frozen', False):
    # 打包后的exe
    APP_DIR = os.path.dirname(sys.executable)
else:
    # 开发环境
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

LOGO_PATH = os.path.join(APP_DIR, "spic_logo.png")
DB_PATH = os.path.join(APP_DIR, "eparser.db")

# --------------- 解析线程 ----------------
class ParseThread(QThread):
    finished = Signal(dict, str)
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, filepath: str):
        super().__init__()
        self.filepath = filepath

    def run(self):
        try:
            self.progress.emit(Constants.PROGRESS_STEPS[0])
            result = parse_efile(self.filepath)
            self.progress.emit(Constants.PROGRESS_STEPS[1])
            # 保存到数据库
            save_result(result)
            self.finished.emit(result, self.filepath)
            self.progress.emit(Constants.PROGRESS_STEPS[2])
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
        self.setWindowTitle(Constants.WINDOW_TITLE)
        self.setWindowIcon(QIcon(os.path.join(APP_DIR, "spic_icon.ico")))
        self.setGeometry(100, 100, *Constants.WINDOW_SIZE)

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
                    logo_pixmap = logo_pixmap.scaled(*Constants.LOGO_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.logo_label.setPixmap(logo_pixmap)
            except Exception:
                self.logo_label.setText("SPIC")
        else:
            self.logo_label.setText("SPIC")
        header_layout.addWidget(self.logo_label)

        title_layout = QVBoxLayout()
        self.main_title = QLabel("国家电投云南国际  昆明生产运营中心 南网102-e文件解析工具")
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
        self.browse_button.setMinimumWidth(Constants.BUTTON_MIN_WIDTH)
        self.browse_button.clicked.connect(self.browseFile)
        button_layout.addWidget(self.browse_button)

        self.parse_button = QPushButton("解析")
        self.parse_button.setMinimumWidth(Constants.BUTTON_MIN_WIDTH)
        self.parse_button.setEnabled(False)
        self.parse_button.clicked.connect(self.parseFile)
        button_layout.addWidget(self.parse_button)

        # 添加数据库管理按钮到按钮行
        self.db_manage_button = QPushButton("数据库管理")
        self.db_manage_button.setMinimumWidth(Constants.BUTTON_MIN_WIDTH)
        self.db_manage_button.clicked.connect(self.openDatabaseManager)
        button_layout.addWidget(self.db_manage_button)

        self.export_button = QPushButton("导出报告")
        self.export_button.setMinimumWidth(Constants.BUTTON_MIN_WIDTH)
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.exportReport)
        button_layout.addWidget(self.export_button)

        self.export_csv_button = QPushButton("导出CSV")
        self.export_csv_button.setMinimumWidth(Constants.BUTTON_MIN_WIDTH)
        self.export_csv_button.setEnabled(False)
        self.export_csv_button.clicked.connect(self.exportCSV)
        button_layout.addWidget(self.export_csv_button)

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
        self.status_label.setStyleSheet("padding: 8px; background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ff0000, stop: 1 #00ff00); border-radius: 5px; border: 1px solid #d0d0d0;")
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


        # Status bar
        self.statusBar = QStatusBar()
        self.statusBar.showMessage(f"  国家电投云南国际  昆明生产运营中心 版权所有 | Ver: {Constants.APP_VERSION} | 联系电话: 0871-65666603")
        self.setStatusBar(self.statusBar)

        self.thread = None

        # Theme check timer
        self.theme_timer = QTimer()
        self.theme_timer.timeout.connect(self.check_theme_change)
        self.theme_timer.start(Constants.THEME_CHECK_INTERVAL)

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
        self.section_table.setMaximumHeight(Constants.TABLE_MAX_HEIGHT)
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


    # -------------- Raw 内容显示改造 --------------
    def displayRaw(self, result: Dict[str, Any]):
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
        content = self.read_file_content(result["filename"])
        self.raw_text.setPlainText(content)

    def read_file_content(self, filepath: str) -> str:
        """读取文件内容，支持多种编码"""
        for encoding in Constants.ENCODINGS:
            try:
                with open(filepath, "r", encoding=encoding) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, UnicodeError, LookupError):
                continue
        else:
            return "无法读取文件内容：不支持的文件编码"

        if len(content) > Constants.MAX_RAW_CONTENT_LENGTH:
            content = content[:Constants.MAX_RAW_CONTENT_LENGTH] + f"\n\n... (内容已截断，原始文件大小: {len(content)} 字节)"

        return content

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
                    f.write(f"版本: {Constants.APP_VERSION}\n")
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
                    f.write("国家电投云南国际  昆明生产运营中心 版权所有\n")
                    f.write(f"版本: {Constants.APP_VERSION}\n")
                    f.write("作者：陈丰 电话：0871-65666603\n")
                    f.write("报告生成完成\n")
                    f.write("=" * 60 + "\n")

                QMessageBox.information(self, "成功", "报告已成功导出！")
            except Exception as e:
                QMessageBox.critical(self, "错误", "导出失败:\n" + str(e))

    # -------------- 导出CSV --------------
    def exportCSV(self):
        if self.current_result is None:
            return

        filepath, _ = QFileDialog.getSaveFileName(self, "保存CSV文件", "", "CSV文件 (*.csv);;所有文件 (*.*)")

        if filepath:
            try:
                import csv
                # 使用UTF-8 with BOM编码，以确保Excel等应用程序正确识别中文
                with open(filepath, "w", newline="", encoding="utf-8-sig") as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # 写入文件信息
                    writer.writerow(["文件信息"])
                    writer.writerow(["文件名", os.path.basename(self.current_result["filename"])])
                    writer.writerow(["解析时间", self.current_result["parse_time"]])
                    writer.writerow([])
                    
                    # 写入系统信息
                    writer.writerow(["系统信息"])
                    for key, value in self.current_result["header"].items():
                        writer.writerow([key, value])
                    writer.writerow([])
                    
                    # 写入统计信息
                    writer.writerow(["统计信息"])
                    total_sections = len(self.current_result["sections"])
                    total_tables = sum(len(s["tables"]) for s in self.current_result["sections"])
                    total_rows = sum(sum(t["row_count"] for t in s["tables"]) for s in self.current_result["sections"])
                    writer.writerow(["数据段数量", str(total_sections)])
                    writer.writerow(["数据表数量", str(total_tables)])
                    writer.writerow(["总数据行数", str(total_rows)])
                    writer.writerow([])
                    
                    # 写入数据段和数据表信息
                    for idx, section in enumerate(self.current_result["sections"], 1):
                        writer.writerow([f"数据段 {idx}: {section['type']}"])
                        writer.writerow(["标签", section["tag"]])
                        writer.writerow(["场站", section["station"]])
                        writer.writerow(["日期", section["date"]])
                        writer.writerow(["时间", section["time"]])
                        writer.writerow(["数据表数量", str(len(section["tables"]))])
                        writer.writerow(["总行数", str(sum(t["row_count"] for t in section["tables"]))])
                        writer.writerow([])
                        
                        for table_idx, table in enumerate(section["tables"], 1):
                            writer.writerow([f"数据表 {table_idx} ({table['row_count']} 行)"])
                            writer.writerow(["表头:"] + table["header"])
                            writer.writerow([])
                            
                            # 写入数据行
                            for row_idx, row_data in enumerate(table["rows"], 1):
                                row_values = [str(row_idx)] + [str(row_data.get(header, "")) for header in table["header"]]
                                writer.writerow(row_values)
                            
                            writer.writerow([])

                QMessageBox.information(self, "成功", "CSV文件已成功导出！")
            except Exception as e:
                QMessageBox.critical(self, "错误", "CSV导出失败:\n" + str(e))

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
        self.status_label.setStyleSheet("padding: 8px; background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ff0000, stop: 1 #00ff00); border-radius: 5px; border: 1px solid #d0d0d0;")

        self.thread = ParseThread(self.filepath)
        self.thread.finished.connect(self.onParseFinished)
        self.thread.error.connect(self.onParseError)
        self.thread.progress.connect(self.onProgress)
        self.thread.start()

    # -------------- 解析进度 --------------
    def onProgress(self, value: int):
        self.progress_bar.setValue(value)

    # -------------- 解析错误 --------------
    def onParseError(self, error_msg: str):
        self.progress_bar.setVisible(False)
        self.status_label.setText("解析失败: " + error_msg)
        self.status_label.setStyleSheet("padding: 8px; background: #ffebee; border-radius: 5px; border: 1px solid #ef9a9a;")
        QMessageBox.critical(self, "解析错误", "解析E文件时出错:\n" + error_msg)
        self.parse_button.setEnabled(True)
        self.browse_button.setEnabled(True)

    # -------------- 解析完成 --------------
    def onParseFinished(self, result: Dict[str, Any], filepath: str):
        try:
            self.current_result = result
            self.progress_bar.setVisible(False)
            self.status_label.setText("解析完成！")
            self.status_label.setStyleSheet("padding: 8px; background: #e8f5e9; border-radius: 5px; border: 1px solid #a5d6a7;")

            self.displaySummary(result)
            self.displayDataSections(result)
            self.displayRaw(result)

            self.parse_button.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.export_button.setEnabled(True)
            self.export_csv_button.setEnabled(True)
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_label.setText("显示数据时出错: " + str(e))
            self.status_label.setStyleSheet("padding: 8px; background: #ffebee; border-radius: 5px; border: 1px solid #ef9a9a;")
            QMessageBox.critical(self, "显示错误", "解析成功但显示数据时出错:\n" + str(e))
            self.parse_button.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.export_csv_button.setEnabled(True)

    # -------------- 显示摘要信息 --------------
    def displaySummary(self, result: Dict[str, Any]):
        self.info_table.setRowCount(0)
        self.info_table.setRowCount(6)

        self.info_table.setItem(0, 0, QTableWidgetItem("文件名"))
        self.info_table.setItem(0, 1, QTableWidgetItem(os.path.basename(result["filename"])))

        self.info_table.setItem(1, 0, QTableWidgetItem("解析时间"))
        self.info_table.setItem(1, 1, QTableWidgetItem(result["parse_time"]))

        self.info_table.setItem(2, 0, QTableWidgetItem("System"))
        self.info_table.setItem(2, 1, QTableWidgetItem(safe_get(result["header"], "System")))

        self.info_table.setItem(3, 0, QTableWidgetItem("Version"))
        self.info_table.setItem(3, 1, QTableWidgetItem(safe_get(result["header"], "Version")))

        self.info_table.setItem(4, 0, QTableWidgetItem("Code"))
        self.info_table.setItem(4, 1, QTableWidgetItem(safe_get(result["header"], "Code")))

        self.info_table.setItem(5, 0, QTableWidgetItem("Data"))
        self.info_table.setItem(5, 1, QTableWidgetItem(safe_get(result["header"], "Data")))

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
    def displayDataSections(self, result: Dict[str, Any]):
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
    def onSectionClicked(self, row: int, column: int):
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
            max_display_rows = min(row_count, Constants.MAX_DISPLAY_ROWS)
        else:
            max_display_rows = row_count

        self.data_table.setRowCount(max_display_rows)

        for row_idx in range(max_display_rows):
            row_data = table["rows"][row_idx]
            for col_idx, header in enumerate(table["header"]):
                value = row_data.get(header, "")
                self.data_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        if row_count > max_display_rows:
            self.status_label.setText(f"已显示 {max_display_rows} 行 (共 {row_count} 行，限制显示以提高性能)")
            self.status_label.setStyleSheet("padding: 8px; background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ff0000, stop: 1 #00ff00); border-radius: 5px; border: 1px solid #d0d0d0;")
        else:
            self.status_label.setText(f"已加载 {row_count} 行数据")
            self.status_label.setStyleSheet("padding: 8px; background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ff0000, stop: 1 #00ff00); border-radius: 5px; border: 1px solid #d0d0d0;")

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
        QHeaderView::section { background-color: #0078d4; color: white; padding: 5px; border: 1px solid #005a9e; }
        QPushButton { background-color: #0078d4; color: white; padding: 8px; border-radius: 5px; }
        QPushButton:hover { background-color: #1e8ad6; }
        QPushButton:disabled { background-color: #4a4a4a; color: #808080; }
        QProgressBar { border: 2px solid #3d3d3d; border-radius: 5px; background-color: #d0d0d0; color: #e0e0e0; }
        QProgressBar::chunk { background-color: #0078d4; }
        QTabWidget::pane { border: 2px solid #3d3d3d; background-color: #2d2d2d; }
        QTabBar::tab { background-color: #2d2d2d; color: #e0e0e0; padding: 10px 20px; }
        QTabBar::tab:selected { background-color: #0078d4; color: white; }
        QGroupBox { border: 2px solid #3d3d3d; border-radius: 5px; margin-top: 10px; color: #e0e0e0; font-weight: bold; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        QTextEdit { background-color: #1e1e1e; color: #e0e0e0; border: 1px solid #3d3d3d; border-radius: 5px; padding: 10px; font-family: "Consolas"; }
        QStatusBar { background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ff0000, stop: 1 #00ff00); color: white; }
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
        QProgressBar { border: 2px solid #d0d0d0; border-radius: 5px; text-align: center; background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ff0000, stop: 1 #00ff00); color: #000; }
        QProgressBar::chunk { background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ff0000, stop: 1 #00ff00); }
        QTabWidget::pane { border: 2px solid #d0d0d0; background-color: #fff; }
        QTabBar::tab { background-color: #f0f0f0; color: #000; padding: 10px 20px; border: 1px solid #d0d0d0; border-bottom: none; border-top-left-radius: 5px; border-top-right-radius: 5px; }
        QTabBar::tab:selected { background-color: #0078d4; color: white; }
        QGroupBox { border: 2px solid #d0d0d0; border-radius: 5px; margin-top: 10px; color: #000; font-weight: bold; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        QTextEdit { background-color: #fff; color: #000; border: 1px solid #d0d0d0; border-radius: 5px; padding: 10px; font-family: "Consolas"; }
        QStatusBar { background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ff0000, stop: 1 #00ff00); color: white; }
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