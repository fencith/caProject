import sys
import os
import re
import json
import logging
import traceback
import tarfile
import gzip
import sqlite3
from io import BytesIO
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart

# Import PySide6 instead of PyQt6
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QFileDialog, QLabel, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QSplitter, QGroupBox, QCheckBox, QComboBox, QSpinBox,
    QDoubleSpinBox, QRadioButton, QButtonGroup, QMessageBox,
    QStatusBar, QToolBar, QFrame, QSizePolicy, QScrollArea,
    QGridLayout, QFormLayout, QPlainTextEdit, QToolButton, QMenu
)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer, QSettings, QStandardPaths
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QAction, QDesktopServices, QClipboard
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QCategoryAxis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qt_app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EFileParser:
    """Enhanced E-file parser with comprehensive validation and error handling"""

    def __init__(self):
        self.validation_results = []
        self.parsed_data = {}
        self.file_info = {}

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse E-file with comprehensive validation"""
        try:
            self.validation_results = []
            self.parsed_data = {}
            self.file_info = {}

            # Check if it's a tar.gz file
            if file_path.endswith('.tar.gz'):
                return self._parse_tar_gz_file(file_path)

            # Read file content
            content = self._read_file_content(file_path)
            if content is None:
                return {'error': 'Unable to read file content'}

            # Basic file info
            self.file_info = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'parse_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Parse header
            header_data = self._parse_header(content)
            if not header_data:
                return {'error': 'Invalid file header'}

            # Parse data section
            data_section = self._extract_data_section(content)
            if not data_section:
                return {'error': 'No data section found'}

            # Parse data records
            data_records = self._parse_data_records(data_section)

            # Validate data
            self._validate_data(header_data, data_records)

            self.parsed_data = {
                'header': header_data,
                'data_records': data_records,
                'validation_results': self.validation_results,
                'file_info': self.file_info
            }

            return self.parsed_data

        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {str(e)}")
            return {'error': str(e), 'traceback': traceback.format_exc()}

    def _read_file_content(self, file_path: str) -> Optional[str]:
        """Read file content with multiple encoding attempts"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    # Try to decode to check if it's valid
                    content.encode('utf-8')
                    return content
            except (UnicodeDecodeError, UnicodeEncodeError):
                continue

        # If all encodings fail, try binary mode
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                # Try to decode as latin-1 (lossless)
                return content.decode('latin-1')
        except Exception:
            return None

    def _parse_tar_gz_file(self, file_path: str) -> Dict[str, Any]:
        """Parse tar.gz file containing E-files"""
        try:
            self.file_info = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'parse_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Extract and parse all files in the archive
            all_records = []
            files_parsed = 0

            with tarfile.open(file_path, 'r:gz') as tar:
                for member in tar.getmembers():
                    if member.isfile() and (member.name.endswith('.dat') or member.name.endswith('.txt')):
                        try:
                            # Extract file content
                            f = tar.extractfile(member)
                            if f:
                                content = f.read().decode('latin-1', errors='ignore')

                                # Parse header
                                header_data = self._parse_header(content)
                                if header_data:
                                    # Parse data section
                                    data_section = self._extract_data_section(content)
                                    if data_section:
                                        # Parse data records
                                        data_records = self._parse_data_records(data_section)
                                        all_records.extend(data_records)
                                        files_parsed += 1

                        except Exception as e:
                            logger.warning(f"Error parsing file {member.name} in archive: {str(e)}")
                            continue

            # Validate combined data
            self._validate_data({}, all_records)

            self.parsed_data = {
                'header': {'archive_info': f'Parsed {files_parsed} files from archive'},
                'data_records': all_records,
                'validation_results': self.validation_results,
                'file_info': self.file_info,
                'archive_stats': {
                    'total_files': files_parsed,
                    'total_records': len(all_records)
                }
            }

            return self.parsed_data

        except Exception as e:
            logger.error(f"Error parsing tar.gz file {file_path}: {str(e)}")
            return {'error': str(e), 'traceback': traceback.format_exc()}
    
    def _parse_header(self, content: str) -> Optional[Dict]:
        """Parse file header with validation - supports multiple formats"""
        # Try original format first
        header_pattern = r'#.*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
        match = re.search(header_pattern, content)

        if match:
            return {
                'timestamp': match.group(1),
                'original_content': match.group(0),
                'format': 'original'
            }

        # Try OMS format
        oms_pattern = r'<!System=OMS.*?Data=(\d+\.\d+)!>'
        oms_match = re.search(oms_pattern, content)

        if oms_match:
            # Extract additional info from OMS format
            data_section_match = re.search(r'<(\w+)::(\w+)\.(\w+)\s+Date=\'([^\']+)\'\s+Time=\'([^\']+)\'>', content)
            if data_section_match:
                return {
                    'system': 'OMS',
                    'version': oms_match.group(1),
                    'data_type': data_section_match.group(1),
                    'region': data_section_match.group(2),
                    'station': data_section_match.group(3),
                    'date': data_section_match.group(4),
                    'time': data_section_match.group(5),
                    'format': 'OMS'
                }

        return None
    
    def _extract_data_section(self, content: str) -> Optional[str]:
        """Extract data section from file"""
        # Look for data section markers - original format
        data_start = content.find('#数据开始')
        if data_start == -1:
            data_start = content.find('#Data Start')

        # Look for OMS format column headers (starts with @)
        if data_start == -1:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('@'):
                    data_start = content.find(line)
                    break

        if data_start != -1:
            return content[data_start:]
        return None
    
    def _parse_data_records(self, data_section: str) -> List[Dict]:
        """Parse individual data records"""
        records = []
        lines = data_section.split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Handle OMS format (starts with #)
            if line.startswith('#'):
                # OMS format: #	seq	value1	value2	value3...
                parts = line[1:].strip().split('\t')  # Remove # and split by tab
                if len(parts) >= 2:
                    try:
                        record = {
                            'line_number': line_num,
                            'timestamp': parts[0],  # Sequence number as timestamp
                            'values': [float(v) for v in parts[1:]],
                            'raw_line': line
                        }
                        records.append(record)
                    except ValueError as e:
                        self.validation_results.append({
                            'type': 'data_error',
                            'line': line_num,
                            'message': f'Invalid data format: {str(e)}',
                            'severity': 'error'
                        })
            else:
                # Original format: timestamp,value1,value2,...
                parts = line.split(',')
                if len(parts) >= 2:
                    try:
                        record = {
                            'line_number': line_num,
                            'timestamp': parts[0],
                            'values': [float(v) for v in parts[1:]],
                            'raw_line': line
                        }
                        records.append(record)
                    except ValueError as e:
                        self.validation_results.append({
                            'type': 'data_error',
                            'line': line_num,
                            'message': f'Invalid data format: {str(e)}',
                            'severity': 'error'
                        })

        return records
    
    def _validate_data(self, header: Dict, records: List[Dict]):
        """Validate parsed data"""
        # Check for missing data
        if not records:
            self.validation_results.append({
                'type': 'missing_data',
                'message': 'No data records found',
                'severity': 'error'
            })
        
        # Check timestamp consistency
        if records:
            first_ts = records[0]['timestamp']
            last_ts = records[-1]['timestamp']
            
            if first_ts >= last_ts:
                self.validation_results.append({
                    'type': 'timestamp_error',
                    'message': f'Timestamp order error: {first_ts} >= {last_ts}',
                    'severity': 'warning'
                })
        
        # Check for duplicate timestamps
        timestamps = [r['timestamp'] for r in records]
        duplicates = [t for t in set(timestamps) if timestamps.count(t) > 1]
        if duplicates:
            self.validation_results.append({
                'type': 'duplicate_timestamps',
                'message': f'Duplicate timestamps found: {duplicates}',
                'severity': 'warning'
            })

class ParseWorker(QObject):
    """Worker thread for file parsing"""
    finished = Signal(dict)
    progress = Signal(int, str)
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.parser = EFileParser()
    
    def run(self):
        """Run parsing in background thread"""
        try:
            self.progress.emit(10, "开始解析文件...")
            
            # Parse file
            result = self.parser.parse_file(self.file_path)
            
            if 'error' in result:
                self.finished.emit({'error': result['error']})
            else:
                self.progress.emit(100, "解析完成")
                self.finished.emit(result)
                
        except Exception as e:
            logger.error(f"Worker error: {str(e)}")
            self.finished.emit({'error': str(e)})

class DatabaseManager:
    """SQLite database manager for storing parsed data"""

    def __init__(self, db_path="efile_parser.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create files table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE,
                    file_name TEXT,
                    file_size INTEGER,
                    parse_time TEXT,
                    record_count INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create records table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER,
                    timestamp TEXT,
                    value1 REAL,
                    value2 REAL,
                    value3 REAL,
                    value4 REAL,
                    raw_line TEXT,
                    FOREIGN KEY (file_id) REFERENCES files (id)
                )
            ''')

            # Create validation_results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS validation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER,
                    result_type TEXT,
                    message TEXT,
                    severity TEXT,
                    FOREIGN KEY (file_id) REFERENCES files (id)
                )
            ''')

            conn.commit()

    def save_parse_result(self, result: dict) -> int:
        """Save parsing result to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Insert file info
            file_info = result['file_info']
            cursor.execute('''
                INSERT OR REPLACE INTO files
                (file_path, file_name, file_size, parse_time, record_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                file_info['file_path'],
                file_info['file_name'],
                file_info['file_size'],
                file_info['parse_time'],
                len(result.get('data_records', []))
            ))

            file_id = cursor.lastrowid

            # Insert records
            records = result.get('data_records', [])
            for record in records:
                cursor.execute('''
                    INSERT INTO records
                    (file_id, timestamp, value1, value2, value3, value4, raw_line)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_id,
                    record['timestamp'],
                    record['values'][0] if len(record['values']) > 0 else None,
                    record['values'][1] if len(record['values']) > 1 else None,
                    record['values'][2] if len(record['values']) > 2 else None,
                    record['values'][3] if len(record['values']) > 3 else None,
                    record['raw_line']
                ))

            # Insert validation results
            validation_results = result.get('validation_results', [])
            for validation in validation_results:
                cursor.execute('''
                    INSERT INTO validation_results
                    (file_id, result_type, message, severity)
                    VALUES (?, ?, ?, ?)
                ''', (
                    file_id,
                    validation['type'],
                    validation['message'],
                    validation['severity']
                ))

            conn.commit()
            return file_id

    def get_recent_files(self, limit=10) -> List[dict]:
        """Get recently parsed files"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, file_path, file_name, parse_time, record_count
                FROM files
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))

            return [{
                'id': row[0],
                'file_path': row[1],
                'file_name': row[2],
                'parse_time': row[3],
                'record_count': row[4]
            } for row in cursor.fetchall()]

    def get_file_records(self, file_id: int) -> List[dict]:
        """Get records for a specific file"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp, value1, value2, value3, value4, raw_line
                FROM records
                WHERE file_id = ?
                ORDER BY id
            ''', (file_id,))

            return [{
                'timestamp': row[0],
                'values': [v for v in row[1:5] if v is not None],
                'raw_line': row[5]
            } for row in cursor.fetchall()]

class SettingsManager:
    """Manage application settings"""

    def __init__(self):
        self.settings = QSettings("EFileParser", "QtApp")

    def get_recent_files(self) -> List[str]:
        """Get list of recently opened files"""
        files = self.settings.value("recent_files", [])
        return files if isinstance(files, list) else []

    def add_recent_file(self, file_path: str):
        """Add file to recent files list"""
        files = self.get_recent_files()
        if file_path in files:
            files.remove(file_path)
        files.insert(0, file_path)

        # Keep only last 10 files
        files = files[:10]
        self.settings.setValue("recent_files", files)

    def get_window_geometry(self) -> bytes:
        """Get saved window geometry"""
        return self.settings.value("window_geometry", b"")

    def set_window_geometry(self, geometry: bytes):
        """Save window geometry"""
        self.settings.setValue("window_geometry", geometry)

    def get_theme(self) -> str:
        """Get current theme setting"""
        return self.settings.value("theme", "auto")

    def set_theme(self, theme: str):
        """Set theme setting"""
        self.settings.setValue("theme", theme)

class ThemeManager:
    """Manage application themes"""
    
    def __init__(self):
        self.settings = SettingsManager()
        
    def apply_theme(self, app: QApplication):
        """Apply current theme to application"""
        theme = self.settings.get_theme()
        
        if theme == "auto":
            # Use system theme
            app.setStyle("Fusion")
            self._apply_system_colors(app)
        elif theme == "light":
            self._apply_light_theme(app)
        elif theme == "dark":
            self._apply_dark_theme(app)
    
    def _apply_system_colors(self, app: QApplication):
        """Apply system colors"""
        # Let Qt use system colors
        app.setStyle("Fusion")
        
    def _apply_light_theme(self, app: QApplication):
        """Apply light theme"""
        app.setStyle("Fusion")
        palette = QPalette()
        
        # Set light theme colors
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(240, 240, 240))
        palette.setColor(QPalette.AlternateBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(0, 120, 215))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        app.setPalette(palette)
    
    def _apply_dark_theme(self, app: QApplication):
        """Apply dark theme"""
        app.setStyle("Fusion")
        palette = QPalette()
        
        # Set dark theme colors
        palette.setColor(QPalette.Window, QColor(32, 32, 32))
        palette.setColor(QPalette.WindowText, QColor(200, 200, 200))
        palette.setColor(QPalette.Base, QColor(45, 45, 45))
        palette.setColor(QPalette.AlternateBase, QColor(32, 32, 32))
        palette.setColor(QPalette.ToolTipBase, QColor(32, 32, 32))
        palette.setColor(QPalette.ToolTipText, QColor(200, 200, 200))
        palette.setColor(QPalette.Text, QColor(200, 200, 200))
        palette.setColor(QPalette.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ButtonText, QColor(200, 200, 200))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        app.setPalette(palette)

class EFileParserApp(QMainWindow):
    """Main application window"""

    def __init__(self, app_instance):
        super().__init__()

        # Store app instance
        self.app_instance = app_instance

        # Initialize managers
        self.settings_manager = SettingsManager()
        self.theme_manager = ThemeManager()
        self.db_manager = DatabaseManager()

        # Setup UI
        self.init_ui()

        # Apply theme
        self.theme_manager.apply_theme(self.app_instance)

        # Restore window geometry
        geometry = self.settings_manager.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)

        # Set window icon
        logo_path = r"D:\001\eTextDTA\logo\spic-logo.svg"
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        # Initialize parser
        self.parser = EFileParser()
        self.current_file = None
        self.parsed_result = None
        
    def init_ui(self):
        """Initialize the user interface"""
        # Set window properties
        self.setWindowTitle('e文件解析工具')
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        self.create_toolbar()

        # Create main content area
        self.create_main_content(main_layout)

        # Update recent files menu after UI is fully created
        self.update_recent_files_menu()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('就绪')
        
        # Create menu bar
        self.create_menu_bar()
        
    def create_toolbar(self):
        """Create application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Open file action
        open_action = QAction("打开文件", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        # Recent files button with menu
        self.recent_button = QToolButton()
        self.recent_button.setText("最近文件")
        self.recent_button.setPopupMode(QToolButton.InstantPopup)
        self.recent_menu = self.recent_button.menu() or self.recent_button.setMenu(QMenu())
        self.recent_menu = QMenu("最近文件")
        self.recent_button.setMenu(self.recent_menu)
        toolbar.addWidget(self.recent_button)
        
        # Theme selector
        theme_label = QLabel("主题:")
        toolbar.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["自动", "浅色", "深色"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        toolbar.addWidget(self.theme_combo)
        
        # Separator
        toolbar.addSeparator()

        # Batch action (limited to 10 items)
        batch_action = QAction("批量", self)
        batch_action.triggered.connect(self.batch_test_files)
        toolbar.addAction(batch_action)

        # Parse action
        parse_action = QAction("解析文件", self)
        parse_action.triggered.connect(self.parse_current_file)
        toolbar.addAction(parse_action)

        # Export action
        export_action = QAction("导出结果", self)
        export_action.triggered.connect(self.export_results)
        toolbar.addAction(export_action)
        
    def create_main_content(self, layout):
        """Create main content area"""
        # Create splitter for left and right panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - File info and controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Results and visualization
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set sizes
        splitter.setSizes([400, 800])
        
        layout.addWidget(splitter)
        
    def create_left_panel(self):
        """Create left panel with file info and controls"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # File info group
        file_group = QGroupBox("文件信息")
        file_layout = QFormLayout()
        
        self.file_path_label = QLabel("未选择文件")
        self.file_size_label = QLabel("-")
        self.parse_time_label = QLabel("-")
        
        file_layout.addRow("文件路径:", self.file_path_label)
        file_layout.addRow("文件大小:", self.file_size_label)
        file_layout.addRow("解析时间:", self.parse_time_label)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Parse options group
        options_group = QGroupBox("解析选项")
        options_layout = QVBoxLayout()
        
        # Validation options
        self.validate_data_checkbox = QCheckBox("验证数据完整性")
        self.validate_data_checkbox.setChecked(True)
        options_layout.addWidget(self.validate_data_checkbox)
        
        self.check_duplicates_checkbox = QCheckBox("检查重复数据")
        self.check_duplicates_checkbox.setChecked(True)
        options_layout.addWidget(self.check_duplicates_checkbox)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Progress area
        progress_group = QGroupBox("解析进度")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("准备就绪")
        progress_layout.addWidget(self.progress_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        self.parse_button = QPushButton("解析文件")
        self.parse_button.clicked.connect(self.parse_current_file)
        actions_layout.addWidget(self.parse_button)
        
        self.clear_button = QPushButton("清除结果")
        self.clear_button.clicked.connect(self.clear_results)
        actions_layout.addWidget(self.clear_button)
        
        layout.addLayout(actions_layout)
        
        # Recent files
        recent_group = QGroupBox("最近文件")
        recent_layout = QVBoxLayout()
        
        self.recent_files_list = QTextEdit()
        self.recent_files_list.setReadOnly(True)
        self.recent_files_list.setMaximumHeight(100)
        recent_layout.addWidget(self.recent_files_list)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        layout.addStretch()
        
        return panel
        
    def create_right_panel(self):
        """Create right panel with results and visualization"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tab widget for different result views
        self.tab_widget = QTabWidget()
        
        # Summary tab
        self.summary_tab = self.create_summary_tab()
        self.tab_widget.addTab(self.summary_tab, "摘要")
        
        # Data tab
        self.data_tab = self.create_data_tab()
        self.tab_widget.addTab(self.data_tab, "数据")
        
        # Validation tab
        self.validation_tab = self.create_validation_tab()
        self.tab_widget.addTab(self.validation_tab, "验证")
        
        # Charts tab
        self.charts_tab = self.create_charts_tab()
        self.tab_widget.addTab(self.charts_tab, "图表")
        
        layout.addWidget(self.tab_widget)
        
        return panel
        
    def create_summary_tab(self):
        """Create summary tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        layout.addWidget(self.summary_text)
        
        return widget
        
    def create_data_tab(self):
        """Create data tab with table view"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)  # timestamp + 4 data columns
        self.data_table.setHorizontalHeaderLabels(['时间戳', '值1', '值2', '值3', '值4'])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.data_table)
        
        # Data controls
        controls_layout = QHBoxLayout()
        
        self.show_raw_checkbox = QCheckBox("显示原始数据")
        self.show_raw_checkbox.toggled.connect(self.toggle_data_view)
        controls_layout.addWidget(self.show_raw_checkbox)
        
        self.filter_edit = QTextEdit()
        self.filter_edit.setMaximumHeight(30)
        self.filter_edit.setPlaceholderText("过滤条件...")
        controls_layout.addWidget(self.filter_edit)
        
        layout.addLayout(controls_layout)
        
        return widget
        
    def create_validation_tab(self):
        """Create validation tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.validation_table = QTableWidget()
        self.validation_table.setColumnCount(3)
        self.validation_table.setHorizontalHeaderLabels(['类型', '消息', '严重性'])
        self.validation_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.validation_table)
        
        return widget
        
    def create_charts_tab(self):
        """Create charts tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Chart view
        self.chart_view = QChartView()
        # Note: Antialiasing render hint for charts
        layout.addWidget(self.chart_view)
        
        # Chart controls
        controls_layout = QHBoxLayout()
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["折线图", "柱状图", "散点图"])
        controls_layout.addWidget(QLabel("图表类型:"))
        controls_layout.addWidget(self.chart_type_combo)
        
        self.data_series_combo = QComboBox()
        self.data_series_combo.addItems(["所有系列", "系列1", "系列2", "系列3"])
        controls_layout.addWidget(QLabel("数据系列:"))
        controls_layout.addWidget(self.data_series_combo)
        
        layout.addLayout(controls_layout)
        
        return widget
        
    def create_menu_bar(self):
        """Create application menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("文件")
        
        open_action = QAction("打开文件", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        export_action = QAction("导出结果", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menu_bar.addMenu("视图")
        
        theme_action = QAction("主题设置", self)
        theme_action.triggered.connect(self.show_theme_dialog)
        view_menu.addAction(theme_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
    def open_file(self):
        """Open file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择E-File", "", "E-Files (*.dat *.txt *.tar.gz);;All Files (*)"
        )

        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path: str):
        """Load and display file information"""
        self.current_file = file_path
        self.file_path_label.setText(file_path)
        
        # Update file size
        try:
            size = os.path.getsize(file_path)
            self.file_size_label.setText(f"{size:,} 字节")
        except:
            self.file_size_label.setText("无法获取文件大小")
        
        # Add to recent files
        self.settings_manager.add_recent_file(file_path)
        self.update_recent_files_menu()
    
    def parse_current_file(self):
        """Parse the currently loaded file"""
        if not self.current_file:
            QMessageBox.warning(self, "警告", "请先选择一个文件")
            return
        
        # Start parsing in background thread
        self.progress_bar.setValue(0)
        self.progress_label.setText("开始解析...")
        self.parse_button.setEnabled(False)
        
        self.thread = QThread()
        self.worker = ParseWorker(self.current_file)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_parse_finished)
        self.worker.progress.connect(self.on_parse_progress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()
    
    def on_parse_progress(self, value: int, message: str):
        """Handle parsing progress updates"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
    
    def on_parse_finished(self, result: dict):
        """Handle parsing completion"""
        self.parse_button.setEnabled(True)
        self.progress_bar.setValue(100)
        self.progress_label.setText("解析完成")

        if 'error' in result:
            QMessageBox.critical(self, "解析错误", f"解析文件时发生错误:\n{result['error']}")
            return

        # Save to database
        try:
            file_id = self.db_manager.save_parse_result(result)
            logger.info(f"Saved parse result to database with file_id: {file_id}")
        except Exception as e:
            logger.error(f"Failed to save to database: {str(e)}")

        # Store result for export
        self.parsed_result = result

        # Display results
        self.display_results(result)

        # Update status bar
        self.status_bar.showMessage(f"成功解析 {len(result['data_records'])} 条记录，已保存到数据库", 3000)
    
    def display_results(self, result: dict):
        """Display parsing results"""
        # Update file info
        self.parse_time_label.setText(result['file_info']['parse_time'])
        
        # Display summary
        self.display_summary(result)
        
        # Display data table
        self.display_data_table(result['data_records'])
        
        # Display validation results
        self.display_validation_results(result['validation_results'])
        
        # Display charts
        self.display_charts(result['data_records'])
    
    def display_summary(self, result: dict):
        """Display parsing summary"""
        summary = f"""
        <h3>解析摘要</h3>
        <p><strong>文件:</strong> {result['file_info']['file_name']}</p>
        <p><strong>大小:</strong> {result['file_info']['file_size']:,} 字节</p>
        <p><strong>解析时间:</strong> {result['file_info']['parse_time']}</p>
        <p><strong>数据记录:</strong> {len(result['data_records'])} 条</p>
        <p><strong>验证结果:</strong> {len(result['validation_results'])} 个问题</p>
        """
        
        self.summary_text.setHtml(summary)
    
    def display_data_table(self, records: List[dict]):
        """Display data in table"""
        self.data_table.setRowCount(len(records))
        
        for row, record in enumerate(records):
            # Timestamp
            self.data_table.setItem(row, 0, QTableWidgetItem(record['timestamp']))
            
            # Data values
            for col, value in enumerate(record['values'][:4], 1):
                self.data_table.setItem(row, col, QTableWidgetItem(str(value)))
    
    def display_validation_results(self, results: List[dict]):
        """Display validation results"""
        self.validation_table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            self.validation_table.setItem(row, 0, QTableWidgetItem(result['type']))
            self.validation_table.setItem(row, 1, QTableWidgetItem(result['message']))
            self.validation_table.setItem(row, 2, QTableWidgetItem(result['severity']))
    
    def display_charts(self, records: List[dict]):
        """Display data charts"""
        if not records:
            return
        
        # Create chart
        chart = QChart()
        chart.setTitle("数据趋势图")
        
        # Create series for each data column
        series_count = min(4, len(records[0]['values']) if records else 0)
        
        for series_idx in range(series_count):
            series = QLineSeries()
            series.setName(f"系列 {series_idx + 1}")
            
            for record in records:
                if series_idx < len(record['values']):
                    # Convert timestamp to numeric for charting
                    # For simplicity, using index as x-axis
                    x = len(series.pointsVector())
                    y = record['values'][series_idx]
                    series.append(x, y)
            
            chart.addSeries(series)
        
        # Configure axes
        axis_x = QValueAxis()
        axis_x.setTitleText("时间")
        chart.addAxis(axis_x, Qt.AlignBottom)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("数值")
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        # Attach series to axes
        for series in chart.series():
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)
        
        # Set chart to view
        self.chart_view.setChart(chart)
    
    def export_results(self):
        """Export parsing results"""
        if not hasattr(self, 'parsed_result') or not self.parsed_result:
            QMessageBox.warning(self, "警告", "没有可导出的结果")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出结果", "", "PDF Files (*.pdf);;JSON Files (*.json);;Text Files (*.txt)"
        )

        if file_path:
            try:
                if file_path.endswith('.pdf'):
                    self._export_pdf_report(file_path)
                elif file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.parsed_result, f, ensure_ascii=False, indent=2)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(self.summary_text.toPlainText())

                QMessageBox.information(self, "导出成功", f"结果已导出到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"导出时发生错误: {str(e)}")

    def _export_pdf_report(self, file_path: str):
        """Export PDF report with parsing results and charts"""
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("E-File 解析报告", title_style))
        story.append(Spacer(1, 12))

        # File information
        file_info = self.parsed_result['file_info']
        header_data = self.parsed_result['header']

        info_data = [
            ['文件信息', ''],
            ['文件路径', file_info['file_path']],
            ['文件名', file_info['file_name']],
            ['文件大小', f"{file_info['file_size']:,} 字节"],
            ['解析时间', file_info['parse_time']],
        ]

        if 'format' in header_data and header_data['format'] == 'OMS':
            info_data.extend([
                ['数据格式', 'OMS'],
                ['系统版本', header_data.get('version', 'N/A')],
                ['数据类型', header_data.get('data_type', 'N/A')],
                ['地区', header_data.get('region', 'N/A')],
                ['站点', header_data.get('station', 'N/A')],
                ['日期', header_data.get('date', 'N/A')],
                ['时间', header_data.get('time', 'N/A')],
            ])

        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))

        # Statistics
        records = self.parsed_result['data_records']
        validations = self.parsed_result['validation_results']

        stats_data = [
            ['解析统计', ''],
            ['数据记录数', str(len(records))],
            ['验证问题数', str(len(validations))],
            ['成功率', f"{(1 - len(validations)/max(1, len(records)))*100:.1f}%" if records else 'N/A'],
        ]

        stats_table = Table(stats_data, colWidths=[2*inch, 4*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 20))

        # Data sample (first 10 records)
        if records:
            story.append(Paragraph("数据样本 (前10条记录)", styles['Heading2']))
            story.append(Spacer(1, 12))

            # Prepare data for table
            table_data = [['序号', '时间戳', '值1', '值2', '值3', '值4']]
            for i, record in enumerate(records[:10]):
                row = [str(i+1), record['timestamp']]
                for j in range(4):
                    if j < len(record['values']):
                        row.append(f"{record['values'][j]:.3f}")
                    else:
                        row.append('-')
                table_data.append(row)

            data_table = Table(table_data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            data_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'RIGHT'),
            ]))
            story.append(data_table)
            story.append(Spacer(1, 20))

        # Validation results
        if validations:
            story.append(Paragraph("验证结果", styles['Heading2']))
            story.append(Spacer(1, 12))

            validation_data = [['类型', '消息', '严重性']]
            for validation in validations[:10]:  # Limit to first 10
                validation_data.append([
                    validation['type'],
                    validation['message'][:50] + '...' if len(validation['message']) > 50 else validation['message'],
                    validation['severity']
                ])

            validation_table = Table(validation_data, colWidths=[1.5*inch, 4*inch, 1*inch])
            validation_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(validation_table)
            story.append(Spacer(1, 20))

        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1
        )
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        story.append(Paragraph("e文件解析工具 v2.0.0", footer_style))
        story.append(Paragraph("版权所有：国家电投生成运营中心", footer_style))

        # Generate PDF
        doc.build(story)
    
    def clear_results(self):
        """Clear all results"""
        self.summary_text.clear()
        self.data_table.setRowCount(0)
        self.validation_table.setRowCount(0)
        self.chart_view.setChart(QChart())
        self.progress_bar.setValue(0)
        self.progress_label.setText("准备就绪")
    
    def toggle_data_view(self, checked: bool):
        """Toggle between raw and processed data view"""
        # This method would toggle the data display format
        # For now, just a placeholder
        pass

    def update_recent_files_menu(self):
        """Update recent files menu"""
        files = self.settings_manager.get_recent_files()
        self.recent_menu.clear()

        for file_path in files:
            action = QAction(file_path, self)
            action.triggered.connect(lambda _, fp=file_path: self.load_file(fp))
            self.recent_menu.addAction(action)

        # Update recent files list in UI
        recent_text = "\n".join(files[:5])  # Show last 5 files
        self.recent_files_list.setText(recent_text)
    
    def change_theme(self, theme_text: str):
        """Change application theme"""
        theme_map = {"自动": "auto", "浅色": "light", "深色": "dark"}
        theme = theme_map.get(theme_text, "auto")
        
        self.settings_manager.set_theme(theme)
        self.theme_manager.apply_theme(self.app_instance)
    
    def show_theme_dialog(self):
        """Show theme selection dialog"""
        # This could be expanded to a more detailed theme dialog
        QMessageBox.information(self, "主题设置", "主题已应用。重启应用以完全生效。")
    
    def batch_test_files(self):
        """Batch test files (limited to 10 items per category)"""
        test_results = {
            'tar_gz_files': {},
            'dat_files_102e2601': {},
            'dat_files_20260114': {}
        }

        total_tests = 0
        successful_tests = 0

        # Test tar.gz files in 102E文本数据2026.01/ (limit to 10)
        tar_gz_dir = os.path.join(os.getcwd(), '102E文本数据2026.01')
        if os.path.exists(tar_gz_dir):
            self.status_bar.showMessage("正在测试 tar.gz 文件...")
            self.progress_bar.setValue(0)

            tar_gz_files = [f for f in os.listdir(tar_gz_dir) if f.endswith('.tar.gz')][:10]  # Limit to 10
            total_tests += len(tar_gz_files)

            for i, filename in enumerate(tar_gz_files):
                file_path = os.path.join(tar_gz_dir, filename)
                self.progress_bar.setValue(int((i / len(tar_gz_files)) * 33))
                self.progress_label.setText(f"测试 tar.gz: {filename}")

                try:
                    parser = EFileParser()
                    result = parser.parse_file(file_path)

                    if 'error' in result:
                        test_results['tar_gz_files'][filename] = {
                            'status': 'failed',
                            'error': result['error']
                        }
                        logger.error(f"Failed to parse {filename}: {result['error']}")
                    else:
                        test_results['tar_gz_files'][filename] = {
                            'status': 'success',
                            'records': len(result.get('data_records', [])),
                            'files_parsed': result.get('archive_stats', {}).get('total_files', 0)
                        }
                        successful_tests += 1
                        logger.info(f"Successfully parsed {filename}: {len(result.get('data_records', []))} records")

                except Exception as e:
                    test_results['tar_gz_files'][filename] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    logger.error(f"Exception parsing {filename}: {str(e)}")

        # Test dat files in 102E2601/ (limit to 10)
        dat_dir = os.path.join(os.getcwd(), '102E2601')
        if os.path.exists(dat_dir):
            self.status_bar.showMessage("正在测试 102E2601 dat 文件...")
            dat_files = [f for f in os.listdir(dat_dir) if f.endswith('.dat')][:10]  # Limit to 10
            total_tests += len(dat_files)

            for i, filename in enumerate(dat_files):
                file_path = os.path.join(dat_dir, filename)
                self.progress_bar.setValue(33 + int((i / len(dat_files)) * 33))
                self.progress_label.setText(f"测试 dat: {filename}")

                try:
                    parser = EFileParser()
                    result = parser.parse_file(file_path)

                    if 'error' in result:
                        test_results['dat_files_102e2601'][filename] = {
                            'status': 'failed',
                            'error': result['error']
                        }
                        logger.error(f"Failed to parse {filename}: {result['error']}")
                    else:
                        test_results['dat_files_102e2601'][filename] = {
                            'status': 'success',
                            'records': len(result.get('data_records', []))
                        }
                        successful_tests += 1
                        logger.info(f"Successfully parsed {filename}: {len(result.get('data_records', []))} records")

                except Exception as e:
                    test_results['dat_files_102e2601'][filename] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    logger.error(f"Exception parsing {filename}: {str(e)}")

        # Test dat files in 20260114/ subdirectories (limit to 10 total)
        main_dir = os.path.join(os.getcwd(), '20260114')
        if os.path.exists(main_dir):
            self.status_bar.showMessage("正在测试 20260114 dat 文件...")
            subdirs = [d for d in os.listdir(main_dir) if os.path.isdir(os.path.join(main_dir, d))]

            tested_files = 0
            for subdir in subdirs:
                if tested_files >= 10:  # Limit total to 10
                    break

                subdir_path = os.path.join(main_dir, subdir)
                dat_files = [f for f in os.listdir(subdir_path) if f.endswith('.dat')]

                for filename in dat_files:
                    if tested_files >= 10:  # Limit total to 10
                        break

                    file_path = os.path.join(subdir_path, filename)
                    self.progress_label.setText(f"测试 {subdir}: {filename}")

                    try:
                        parser = EFileParser()
                        result = parser.parse_file(file_path)

                        if 'error' in result:
                            test_results['dat_files_20260114'][f"{subdir}/{filename}"] = {
                                'status': 'failed',
                                'error': result['error']
                            }
                            logger.error(f"Failed to parse {subdir}/{filename}: {result['error']}")
                        else:
                            test_results['dat_files_20260114'][f"{subdir}/{filename}"] = {
                                'status': 'success',
                                'records': len(result.get('data_records', []))
                            }
                            successful_tests += 1
                            logger.info(f"Successfully parsed {subdir}/{filename}: {len(result.get('data_records', []))} records")

                    except Exception as e:
                        test_results['dat_files_20260114'][f"{subdir}/{filename}"] = {
                            'status': 'failed',
                            'error': str(e)
                        }
                        logger.error(f"Exception parsing {subdir}/{filename}: {str(e)}")

                    tested_files += 1
                    total_tests += 1

        # Update progress
        self.progress_bar.setValue(100)
        self.progress_label.setText("批量测试完成")

        # Show results summary
        tar_gz_success = sum(1 for r in test_results['tar_gz_files'].values() if r['status'] == 'success')
        dat_102e2601_success = sum(1 for r in test_results['dat_files_102e2601'].values() if r['status'] == 'success')
        dat_20260114_success = sum(1 for r in test_results['dat_files_20260114'].values() if r['status'] == 'success')

        summary = f"""
        <h3>批量测试结果 (最多显示10个文件)</h3>
        <p><strong>tar.gz 文件 (102E文本数据2026.01):</strong> {tar_gz_success}/{len(test_results['tar_gz_files'])} 成功</p>
        <p><strong>dat 文件 (102E2601):</strong> {dat_102e2601_success}/{len(test_results['dat_files_102e2601'])} 成功</p>
        <p><strong>dat 文件 (20260114):</strong> {dat_20260114_success}/{len(test_results['dat_files_20260114'])} 成功</p>
        <p><strong>总计:</strong> {successful_tests}/{total_tests} 成功</p>
        """

        # Show detailed results in summary tab
        self.summary_text.setHtml(summary)
        self.tab_widget.setCurrentIndex(0)  # Switch to summary tab

        # Save detailed results to log
        with open('batch_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)

        self.status_bar.showMessage(f"批量测试完成: {successful_tests}/{total_tests} 成功", 5000)

        # Show message box with summary
        QMessageBox.information(
            self, "批量测试完成",
            f"测试完成! (最多显示10个文件)\n\n"
            f"tar.gz 文件: {tar_gz_success}/{len(test_results['tar_gz_files'])} 成功\n"
            f"102E2601 dat 文件: {dat_102e2601_success}/{len(test_results['dat_files_102e2601'])} 成功\n"
            f"20260114 dat 文件: {dat_20260114_success}/{len(test_results['dat_files_20260114'])} 成功\n"
            f"总计: {successful_tests}/{total_tests} 成功\n\n"
            f"详细结果已保存到 batch_test_results.json"
        )

    def show_about_dialog(self):
        """Show about dialog"""
        about_text = """
        <h2>e文件解析工具</h2>
        <p>版本: 2.0.0</p>
        <p>版权所有：国家电投生成运营中心</p>
        <p>作者：陈丰 联系电话：0871-65666603</p>
        <p>功能: E-File文件解析和分析工具</p>
        <p>支持格式: .dat, .txt, .tar.gz</p>
        """
        QMessageBox.about(self, "关于", about_text)
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Save window geometry
        self.settings_manager.set_window_geometry(self.saveGeometry())
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("E-File Parser Pro")
    app.setOrganizationName("EFileParser")
    app.setOrganizationDomain("efileparser.com")
    
    # Store app instance for theme manager
    app.instance = app
    
    # Create and show main window
    window = EFileParserApp(app)
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
