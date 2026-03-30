# -*- coding: utf-8 -*-
"""
E文件解析工具 - 版本：v2.1.2
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

# PySide6 imports
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem, QGroupBox,
                             QTextEdit, QTabWidget, QStatusBar, QFileDialog, QMessageBox,
                             QDialog, QCheckBox, QProgressBar, QHeaderView, QSplitter)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPixmap, QIcon, QFont


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
        self.db_section_table.setMaximumHeight(150)
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
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            record_id = self.records_table.item(row, 0).text()
            cur.execute("SELECT summary_json FROM parse_results WHERE id = ?", (record_id,))
            result = cur.fetchone()
            conn.close()

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
                        f.write("国家电投云南国际  昆明生产运营中心 版权所有\n")
                        f.write("版本: 2.1.2\n")
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
ICON_PATH = os.path.join(APP_DIR, "spic_icon.ico")
DB_PATH = os.path.join(APP_DIR, "eparser.db")

# 导入数据库工具函数和解析函数
def parse_efile(filename):
    """解析E文件，支持.tar.gz、.lbx和.dat格式"""
    result = {
        "filename": filename,
        "parse_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "header": {},
        "sections": [],
        "tar_info": None,
        "lbx_info": None
    }

    # 检查文件是否存在
    if not os.path.exists(filename):
        raise FileNotFoundError(f"文件不存在: {filename}")

    # 根据文件扩展名选择解析方式
    file_ext = os.path.splitext(filename)[1].lower()

    if file_ext == '.tar' or filename.lower().endswith('.tar.gz') or filename.lower().endswith('.tgz'):
        return parse_tar_file(filename)
    elif file_ext == '.lbx':
        return parse_lbx_file(filename)
    elif file_ext == '.dat':
        return parse_dat_file(filename)
    else:
        raise ValueError(f"不支持的文件格式: {file_ext}")

def parse_tar_file(filename):
    """解析tar.gz文件"""
    result = {
        "filename": filename,
        "parse_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "header": {},
        "sections": [],
        "tar_info": {
            "tar_name": os.path.basename(filename),
            "dat_count": 0,
            "preview": []
        }
    }

    try:
        with tarfile.open(filename, 'r:*') as tar:
            # 获取所有成员文件
            members = tar.getmembers()
            dat_files = [m for m in members if m.name.lower().endswith('.dat')]
            
            result["tar_info"]["dat_count"] = len(dat_files)
            
            # 生成预览内容
            result["tar_info"]["preview"].append(f"压缩包包含 {len(members)} 个文件")
            result["tar_info"]["preview"].append(f"其中 .dat 文件 {len(dat_files)} 个")
            result["tar_info"]["preview"].append("")
            
            for i, member in enumerate(dat_files[:10], 1):
                result["tar_info"]["preview"].append(f"{i}. {member.name} ({member.size} 字节)")
             
            if len(dat_files) > 10:
                result["tar_info"]["preview"].append(f"... 还有 {len(dat_files) - 10} 个文件")
            
            result["tar_info"]["preview"].append("")

            # 辅助：确保提取时不会发生路径遍历攻击
            def _safe_extract_member(tarobj, member, target_dir):
                member_path = os.path.join(target_dir, member.name)
                # 仅允许提取到目标目录及其子目录内
                if not os.path.commonpath([os.path.abspath(target_dir), os.path.abspath(member_path)]) == os.path.abspath(target_dir):
                    raise Exception(f"不安全的 tar 文件成员路径: {member.name}")
                tarobj.extract(member, target_dir)

            # 解压并解析每个.dat文件
            for member in dat_files:
                try:
                    # 提取文件到临时目录
                    with tempfile.TemporaryDirectory() as temp_dir:
                        _safe_extract_member(tar, member, temp_dir)
                        temp_file_path = os.path.join(temp_dir, member.name)
                        
                        # 解析提取的.dat文件
                        dat_result = parse_dat_file(temp_file_path)
                        
                        # 合并结果
                        result["sections"].extend(dat_result["sections"])
                        
                        # 如果是第一个文件，保留header信息
                        if not result["header"] and dat_result["header"]:
                            result["header"] = dat_result["header"]
                        
                except Exception as e:
                    result["tar_info"]["preview"].append(f"警告: 解析文件 {member.name} 时出错: {str(e)}")
                    continue

    except Exception as e:
        raise Exception(f"解析tar文件失败: {str(e)}")

    return result

def parse_lbx_file(filename):
    """解析lbx文件（内部包含多个.dat文件）"""
    result = {
        "filename": filename,
        "parse_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "header": {},
        "sections": [],
        "lbx_info": {
            "lbx_name": os.path.basename(filename),
            "dat_count": 0
        }
    }

    try:
        with open(filename, 'rb') as f:
            content = f.read()
            
        # 查找.dat文件的起始标记
        dat_markers = []
        search_start = 0
        
        while True:
            marker_pos = content.find(b'.dat', search_start)
            if marker_pos == -1:
                break
                
            # 检查标记前是否有足够空间用于长度信息
            if marker_pos >= 4:
                # 读取前4字节作为长度（假设为小端序32位整数）
                length_bytes = content[marker_pos-4:marker_pos]
                try:
                    file_length = int.from_bytes(length_bytes, byteorder='little')
                    if 0 < file_length < 10000000:  # 合理的文件大小范围
                        dat_markers.append((marker_pos - 4, file_length))
                except:
                    pass
            
            search_start = marker_pos + 1

        result["lbx_info"]["dat_count"] = len(dat_markers)

        # 解析每个.dat文件
        for i, (start_pos, length) in enumerate(dat_markers):
            try:
                # 提取.dat文件内容
                dat_content = content[start_pos:start_pos + length + 4]
                
                # 保存到临时文件并解析
                with tempfile.NamedTemporaryFile(mode='wb', suffix='.dat', delete=False) as temp_file:
                    temp_file.write(dat_content)
                    temp_file_path = temp_file.name
                
                try:
                    # 解析临时.dat文件
                    dat_result = parse_dat_file(temp_file_path)
                    
                    # 合并结果
                    result["sections"].extend(dat_result["sections"])
                    
                    # 如果是第一个文件，保留header信息
                    if not result["header"] and dat_result["header"]:
                        result["header"] = dat_result["header"]
                        
                finally:
                    # 删除临时文件
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                        
            except Exception as e:
                continue

    except Exception as e:
        raise Exception(f"解析lbx文件失败: {str(e)}")

    return result

def parse_dat_file(filename):
    """解析单个.dat文件"""
    result = {
        "filename": filename,
        "parse_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "header": {},
        "sections": []
    }

    try:
        # 尝试多种编码
        encodings = ["utf-8", "gbk", "gb2312", "gb18030", "utf-16"]
        content = None
        used_encoding = None

        for encoding in encodings:
            try:
                with open(filename, "r", encoding=encoding) as f:
                    content = f.read()
                used_encoding = encoding
                break
            except (UnicodeDecodeError, UnicodeError, LookupError):
                continue

        if content is None:
            raise Exception("无法读取文件内容：不支持的文件编码")

        # 按行分割
        lines = content.splitlines()
        
        # 解析头部信息
        header_lines = []
        data_start_idx = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("System:") or line.startswith("Version:") or line.startswith("Code:") or line.startswith("Data:"):
                header_lines.append(line)
                data_start_idx = i + 1
            elif line.startswith("System=") or line.startswith("Version=") or line.startswith("Code=") or line.startswith("Data="):
                header_lines.append(line)
                data_start_idx = i + 1
            else:
                break

        # 解析头部
        for line in header_lines:
            if "=" in line:
                key, value = line.split("=", 1)
                result["header"][key.strip()] = value.strip()
            elif ":" in line:
                key, value = line.split(":", 1)
                result["header"][key.strip()] = value.strip()

        # 解析数据段
        current_section = None
        current_table = None
        in_table = False
        table_header = []
        table_rows = []

        for i in range(data_start_idx, len(lines)):
            line = lines[i].strip()
            if not line:
                continue

            # 检查是否是新的数据段开始
            if line.startswith("FD_") or line.startswith("PV_"):
                # 保存前一个表（如果有）
                if current_table and table_header:
                    current_table["rows"] = table_rows
                    current_table["row_count"] = len(table_rows)
                    current_section["tables"].append(current_table)

                # 保存前一个段（如果有）
                if current_section:
                    result["sections"].append(current_section)

                # 开始新的数据段
                parts = line.split()
                if len(parts) >= 4:
                    current_section = {
                        "type": parts[0],
                        "tag": parts[1],
                        "station": parts[2],
                        "date": parts[3],
                        "time": parts[4] if len(parts) > 4 else "",
                        "tables": []
                    }
                    current_table = None
                    in_table = False
                    table_header = []
                    table_rows = []

            # 检查是否是表头
            elif line.startswith("Tag") or line.startswith("Time") or line.startswith("Station"):
                if current_section:
                    # 保存前一个表（如果有）
                    if current_table and table_header:
                        current_table["rows"] = table_rows
                        current_table["row_count"] = len(table_rows)
                        current_section["tables"].append(current_table)

                    # 开始新的表
                    table_header = line.split()
                    current_table = {
                        "header": table_header,
                        "rows": [],
                        "row_count": 0
                    }
                    in_table = True
                    table_rows = []

            # 检查是否是数据行
            elif in_table and current_table:
                # 简单的数据行检测：包含数字或特定格式
                if any(c.isdigit() for c in line) or "," in line or "\t" in line:
                    # 解析数据行
                    if "\t" in line:
                        row_data = line.split("\t")
                    elif "," in line:
                        row_data = line.split(",")
                    else:
                        row_data = line.split()

                    # 构建行字典
                    row_dict = {}
                    for j, value in enumerate(row_data):
                        if j < len(table_header):
                            row_dict[table_header[j]] = value
                        else:
                            row_dict[f"Column_{j}"] = value

                    table_rows.append(row_dict)

        # 保存最后一个表
        if current_table and table_header and table_rows:
            current_table["rows"] = table_rows
            current_table["row_count"] = len(table_rows)
            if current_section:
                current_section["tables"].append(current_table)

        # 保存最后一个段
        if current_section:
            result["sections"].append(current_section)

    except Exception as e:
        raise Exception(f"解析dat文件失败: {str(e)}")

    return result

def init_db():
    """初始化数据库，严格按照南方电网新能源数据上送规范 V3.3修订版（2022.2月）建立表结构"""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. 风力发电机组信息表 (FDJZ)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wind_turbine_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            turbine_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            wind_speed REAL,
            wind_direction REAL,
            ambient_temp REAL,
            nacelle_temp REAL,
            rotor_speed REAL,
            generator_speed REAL,
            yaw_position REAL,
            cable_twist_angle REAL,
            blade1_pitch_angle REAL,
            blade2_pitch_angle REAL,
            blade3_pitch_angle REAL,
            stator_temp REAL,
            bearing_temp REAL,
            gearbox_oil_temp REAL,
            gearbox_bearing_temp REAL,
            gearbox_oil_pressure REAL,
            gearbox_oil_level REAL,
            active_power REAL,
            reactive_power REAL,
            power_factor REAL,
            generator_voltage REAL,
            generator_current REAL,
            grid_voltage REAL,
            grid_current REAL,
            theoretical_power REAL,
            turbine_status INTEGER,
            feeder_line TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, turbine_id, timestamp)
        )
    """)
    
    # 2. 升压站信息表 (SYZXX)
    # 主升压变信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS main_transformer_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            transformer_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            lv_voltage_a REAL,
            lv_voltage_b REAL,
            lv_voltage_c REAL,
            lv_voltage_ab REAL,
            lv_voltage_bc REAL,
            lv_voltage_ca REAL,
            lv_current_a REAL,
            lv_current_b REAL,
            lv_current_c REAL,
            lv_active_power REAL,
            lv_active_power_status INTEGER,
            lv_reactive_power REAL,
            lv_reactive_power_status INTEGER,
            hv_voltage_a REAL,
            hv_voltage_b REAL,
            hv_voltage_c REAL,
            hv_voltage_ab REAL,
            hv_voltage_bc REAL,
            hv_voltage_ca REAL,
            hv_current_a REAL,
            hv_current_b REAL,
            hv_current_c REAL,
            hv_active_power REAL,
            hv_active_power_status INTEGER,
            hv_reactive_power REAL,
            hv_reactive_power_status INTEGER,
            hv_power_factor REAL,
            tap_position INTEGER,
            tap_position_status INTEGER,
            hv_switch_remote_local INTEGER,
            lv_switch_remote_local INTEGER,
            protection_action_total INTEGER,
            protection_device_fault TEXT,
            protection_action_signal TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, transformer_id, timestamp)
        )
    """)
    
    # 并网点信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grid_connection_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            voltage_a REAL,
            voltage_b REAL,
            voltage_c REAL,
            voltage_ab REAL,
            voltage_bc REAL,
            voltage_ca REAL,
            current_a REAL,
            current_b REAL,
            current_c REAL,
            active_power REAL,
            reactive_power REAL,
            power_factor REAL,
            energy_consumption REAL,
            voltage_flicker_a REAL,
            voltage_flicker_b REAL,
            voltage_flicker_c REAL,
            voltage_deviation_a REAL,
            voltage_deviation_b REAL,
            voltage_deviation_c REAL,
            frequency_deviation_a REAL,
            frequency_deviation_b REAL,
            frequency_deviation_c REAL,
            harmonic_thd_a REAL,
            harmonic_thd_b REAL,
            harmonic_thd_c REAL,
            switch_remote_local INTEGER,
            protection_action_total INTEGER,
            control_circuit_break INTEGER,
            reclosing_action INTEGER,
            protection_device_fault TEXT,
            switch_fault INTEGER,
            protection_action_signal TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 升压站母线信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS busbar_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            busbar_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            hv_voltage_a REAL,
            hv_voltage_b REAL,
            hv_voltage_c REAL,
            hv_voltage_ab REAL,
            hv_voltage_bc REAL,
            hv_voltage_ca REAL,
            hv_frequency REAL,
            lv_voltage_a REAL,
            lv_voltage_b REAL,
            lv_voltage_c REAL,
            lv_voltage_ab REAL,
            lv_voltage_bc REAL,
            lv_voltage_ca REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, busbar_name, timestamp)
        )
    """)
    
    # 无功补偿设备信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reactive_compensation_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            device_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            reactive_power REAL,
            current_a REAL,
            current_b REAL,
            current_c REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, device_name, timestamp)
        )
    """)
    
    # 集电线信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feeder_line_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            feeder_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            active_power REAL,
            active_power_status INTEGER,
            reactive_power REAL,
            reactive_power_status INTEGER,
            power_factor REAL,
            voltage_ab REAL,
            voltage_bc REAL,
            voltage_ca REAL,
            current_a REAL,
            current_b REAL,
            current_c REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, feeder_name, timestamp)
        )
    """)
    
    # 断路器信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS circuit_breaker_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            breaker_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            status INTEGER,
            status_quality INTEGER,
            active_power REAL,
            active_power_quality INTEGER,
            reactive_power REAL,
            reactive_power_quality INTEGER,
            power_factor REAL,
            current_a REAL,
            current_b REAL,
            current_c REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, breaker_name, timestamp)
        )
    """)
    
    # 刀闸信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS disconnect_switch_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            switch_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            status INTEGER,
            status_quality INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, switch_name, timestamp)
        )
    """)
    
    # 接地刀闸信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grounding_switch_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            switch_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            status INTEGER,
            status_quality INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, switch_name, timestamp)
        )
    """)
    
    # 等效发电机信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS equivalent_generator_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            generator_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            active_power_quality INTEGER,
            reactive_power REAL,
            reactive_power_quality INTEGER,
            phase_voltage_a REAL,
            phase_current_a REAL,
            max_adjustable_output REAL,
            min_adjustable_output REAL,
            rated_capacity REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, generator_id, timestamp)
        )
    """)
    
    # 3. 风电场总体信息表 (ZTXX)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wind_farm_overall_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            longitude REAL,
            latitude REAL,
            normal_generation_active_capacity REAL,
            normal_generation_reactive_capacity REAL,
            normal_generation_units INTEGER,
            planned_maintenance_active_capacity REAL,
            planned_maintenance_reactive_capacity REAL,
            planned_maintenance_units INTEGER,
            curtailed_active_capacity REAL,
            curtailed_reactive_capacity REAL,
            curtailed_units INTEGER,
            standby_active_capacity REAL,
            standby_reactive_capacity REAL,
            standby_units INTEGER,
            communication_interrupt_active_capacity REAL,
            communication_interrupt_reactive_capacity REAL,
            communication_interrupt_units INTEGER,
            unplanned_outage_active_capacity REAL,
            unplanned_outage_reactive_capacity REAL,
            unplanned_outage_units INTEGER,
            reactive_compensation_availability_rate REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 4. 气象环境信息表 (QXHJ)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS meteorological_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            temp_10m REAL,
            humidity_10m REAL,
            pressure_10m REAL,
            wind_speed_10m REAL,
            wind_direction_10m REAL,
            wind_speed_30m REAL,
            wind_direction_30m REAL,
            wind_speed_50m REAL,
            wind_direction_50m REAL,
            wind_speed_70m REAL,
            wind_direction_70m REAL,
            hub_height_wind_speed REAL,
            hub_height_wind_direction REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 5. AGC信息表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agc_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            max_output_limit REAL,
            min_output_limit REAL,
            response_rate REAL,
            target_value_return REAL,
            status INTEGER,
            remote_local INTEGER,
            increase_lock INTEGER,
            decrease_lock INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 6. AVC信息表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS avc_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            hv_bus_voltage_upper_limit REAL,
            hv_bus_voltage_lower_limit REAL,
            status INTEGER,
            remote_local INTEGER,
            increase_lock INTEGER,
            decrease_lock INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 7. 短期功率预测信息表 (DQYC)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS short_term_forecast_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            forecast_date DATE NOT NULL,
            forecast_time TIME NOT NULL,
            timestamp DATETIME NOT NULL,
            forecast_power REAL,
            planned_capacity REAL,
            operating_units INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, forecast_date, forecast_time, timestamp)
        )
    """)
    
    # 8. 超短期功率预测信息表 (CDQYC)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ultra_short_term_forecast_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            forecast_date DATE NOT NULL,
            forecast_time TIME NOT NULL,
            timestamp DATETIME NOT NULL,
            forecast_power REAL,
            operating_capacity REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, forecast_date, forecast_time, timestamp)
        )
    """)
    
    # 9. 统计信息表 (TJXX)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS statistics_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            turbine_count INTEGER,
            installed_capacity REAL,
            total_active_power REAL,
            total_reactive_power REAL,
            available_generation_power REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 10. 光伏箱变/方阵信息表 (XB-FZ)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pv_transformer_array_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            transformer_id TEXT,
            array_id TEXT,
            timestamp DATETIME NOT NULL,
            lv_voltage_a REAL,
            lv_current_a REAL,
            lv_active_power REAL,
            hv_voltage_a REAL,
            hv_voltage_b REAL,
            hv_voltage_c REAL,
            hv_voltage_ab REAL,
            hv_voltage_bc REAL,
            hv_voltage_ca REAL,
            hv_current_a REAL,
            hv_current_b REAL,
            hv_current_c REAL,
            hv_active_power REAL,
            hv_reactive_power REAL,
            hv_power_factor REAL,
            winding_temp REAL,
            daily_energy REAL,
            monthly_energy REAL,
            yearly_energy REAL,
            cumulative_energy REAL,
            theoretical_max_power REAL,
            reactive_output_range REAL,
            transformer_status INTEGER,
            dc_overvoltage INTEGER,
            ac_overvoltage INTEGER,
            ac_undervoltage INTEGER,
            protection_signals TEXT,
            feeder_line TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, transformer_id, array_id, timestamp)
        )
    """)
    
    # 11. 光伏逆变器/汇流箱信息表 (NBQ-HLX)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pv_inverter_combiner_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            inverter_id TEXT,
            combiner_id TEXT,
            timestamp DATETIME NOT NULL,
            dc_voltage REAL,
            dc_current REAL,
            dc_power REAL,
            ac_voltage_a REAL,
            ac_voltage_b REAL,
            ac_voltage_c REAL,
            ac_voltage_ab REAL,
            ac_voltage_bc REAL,
            ac_voltage_ca REAL,
            ac_current_a REAL,
            ac_current_b REAL,
            ac_current_c REAL,
            ac_active_power REAL,
            ac_reactive_power REAL,
            ac_power_factor REAL,
            inverter_temp REAL,
            daily_energy REAL,
            monthly_energy REAL,
            yearly_energy REAL,
            cumulative_energy REAL,
            max_output_power REAL,
            reactive_output_range REAL,
            grid_status INTEGER,
            fault_status INTEGER,
            maintenance_status INTEGER,
            curtailment_status INTEGER,
            normal_shutdown_status INTEGER,
            communication_interrupt_status INTEGER,
            dc_overvoltage INTEGER,
            ac_overvoltage INTEGER,
            ac_undervoltage INTEGER,
            protection_signals TEXT,
            feeder_line TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, inverter_id, combiner_id, timestamp)
        )
    """)
    
    # 12. 光伏电站总体信息表 (ZTXX)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pv_farm_overall_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            longitude REAL,
            latitude REAL,
            normal_generation_active_capacity REAL,
            normal_generation_reactive_capacity REAL,
            normal_generation_units INTEGER,
            planned_maintenance_active_capacity REAL,
            planned_maintenance_reactive_capacity REAL,
            planned_maintenance_units INTEGER,
            curtailed_active_capacity REAL,
            curtailed_reactive_capacity REAL,
            curtailed_units INTEGER,
            standby_active_capacity REAL,
            standby_reactive_capacity REAL,
            standby_units INTEGER,
            communication_interrupt_active_capacity REAL,
            communication_interrupt_reactive_capacity REAL,
            communication_interrupt_units INTEGER,
            unplanned_outage_active_capacity REAL,
            unplanned_outage_reactive_capacity REAL,
            unplanned_outage_units INTEGER,
            actual_grid_capacity REAL,
            total_output REAL,
            controllable_capacity REAL,
            theoretical_max_active_power REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 13. 光伏气象环境信息表 (QXHJ)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pv_meteorological_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            total_radiation REAL,
            direct_radiation REAL,
            diffuse_radiation REAL,
            reflected_radiation REAL,
            temperature REAL,
            pv_module_temperature REAL,
            pressure REAL,
            humidity REAL,
            wind_speed REAL,
            wind_direction REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 14. 太阳跟踪系统信息表 (TYGZ)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS solar_tracking_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            height_angle REAL,
            azimuth_angle REAL,
            operation_status INTEGER,
            auto_manual_status INTEGER,
            anti_wind_snow_status INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 15. 解析结果主表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parse_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            parse_time TEXT NOT NULL,
            summary_json TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_result(result):
    """保存解析结果到数据库，严格按照规范存储到对应表中"""
    import sqlite3
    import json
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 保存主记录
    summary_json = json.dumps(result, ensure_ascii=False, indent=2)
    cur.execute("""
        INSERT INTO parse_results (filename, parse_time, summary_json)
        VALUES (?, ?, ?)
    """, (result["filename"], result["parse_time"], summary_json))
    
    conn.commit()
    conn.close()

def query_results():
    """查询所有解析结果"""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, filename, parse_time, summary_json FROM parse_results ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

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
        self.setWindowIcon(QIcon(ICON_PATH))
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
        self.browse_button.setMinimumWidth(100)
        self.browse_button.clicked.connect(self.browseFile)
        button_layout.addWidget(self.browse_button)

        self.parse_button = QPushButton("解析")
        self.parse_button.setMinimumWidth(100)
        self.parse_button.setEnabled(False)
        self.parse_button.clicked.connect(self.parseFile)
        button_layout.addWidget(self.parse_button)

        # 添加数据库管理按钮到按钮行
        self.db_manage_button = QPushButton("数据库管理")
        self.db_manage_button.setMinimumWidth(100)
        self.db_manage_button.clicked.connect(self.openDatabaseManager)
        button_layout.addWidget(self.db_manage_button)

        self.export_button = QPushButton("导出报告")
        self.export_button.setMinimumWidth(100)
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.exportReport)
        button_layout.addWidget(self.export_button)

        self.export_csv_button = QPushButton("导出CSV")
        self.export_csv_button.setMinimumWidth(100)
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
        self.statusBar.showMessage("  国家电投云南国际  昆明生产运营中心 版权所有 | Ver: 2.1 | 联系电话: 0871-65666603")
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
                    f.write("版本: 2.1.2\n")
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
                    f.write("版本: 2.1.2\n")
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
        self.status_label.setStyleSheet("padding: 8px; background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ff0000, stop: 1 #00ff00); border-radius: 5px; border: 1px solid #d0d0d0;")

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
            self.status_label.setStyleSheet("padding: 8px; background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ff0000, stop: 1 #00ff00); border-radius: 5px; border: 1px solid #d0d0d0;")
        else:
            self.status_label.setText("已加载 " + str(row_count) + " 行数据")
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
