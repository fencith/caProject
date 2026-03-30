import sqlite3
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
from pathlib import Path


class DatabaseError(Exception):
    """数据库操作错误异常"""
    pass


class Constants:
    """数据库常量定义"""
    DB_VERSION = "1.0"
    MAX_QUERY_LIMIT = 1000
    BATCH_SIZE = 100


class DatabaseManager:
    """数据库管理器类"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_dir()
    
    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """数据库连接上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 启用字典式访问
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"数据库操作失败: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def init_db(self):
        """初始化数据库"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建解析结果表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parse_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    parse_time TEXT NOT NULL,
                    summary_json TEXT NOT NULL,
                    header_json TEXT NOT NULL,
                    sections_json TEXT NOT NULL,
                    archive_info_json TEXT DEFAULT '{}',
                    file_size INTEGER DEFAULT 0,
                    file_modified TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引提高查询性能
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_parse_results_filename 
                ON parse_results(filename)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_parse_results_parse_time 
                ON parse_results(parse_time)
            ''')
            
            # 插入版本信息
            cursor.execute('''
                INSERT OR IGNORE INTO sqlite_master (type, name, tbl_name, sql)
                VALUES ('table', 'db_version', 'db_version', 'CREATE TABLE db_version(version TEXT)')
            ''')
            
            cursor.execute('''
                INSERT OR REPLACE INTO db_version (version) VALUES (?)
            ''', (Constants.DB_VERSION,))
            
            conn.commit()
    
    def save_result(self, result: Dict[str, Any], file_info: Optional[Dict[str, Any]] = None):
        """保存解析结果到数据库"""
        if not result or 'sections' not in result:
            raise DatabaseError("无效的解析结果")
        
        summary_json = json.dumps(result, ensure_ascii=False, indent=2)
        header_json = json.dumps(result.get("header", {}), ensure_ascii=False, indent=2)
        sections_json = json.dumps(result.get("sections", []), ensure_ascii=False, indent=2)
        
        # 提取压缩包信息（如果有）
        archive_info = result.get("archive_info", {})
        archive_info_json = json.dumps(archive_info, ensure_ascii=False, indent=2)
        
        # 文件信息
        file_size = 0
        file_modified = ""
        if file_info:
            file_size = file_info.get("size", 0)
            file_modified = file_info.get("modified", "")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO parse_results (
                    filename, parse_time, summary_json, header_json, 
                    sections_json, archive_info_json, file_size, file_modified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.get("filename", ""),
                result.get("parse_time", ""),
                summary_json,
                header_json,
                sections_json,
                archive_info_json,
                file_size,
                file_modified
            ))
            conn.commit()
    
    def query_results(self, limit: int = Constants.MAX_QUERY_LIMIT, 
                     offset: int = 0) -> List[Dict[str, Any]]:
        """查询解析结果"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, filename, parse_time, summary_json, archive_info_json
                FROM parse_results 
                ORDER BY id DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            results = []
            for row in rows:
                try:
                    summary = json.loads(row['summary_json'])
                    archive_info = json.loads(row['archive_info_json'])
                    results.append({
                        'id': row['id'],
                        'filename': row['filename'],
                        'parse_time': row['parse_time'],
                        'summary': summary,
                        'archive_info': archive_info
                    })
                except json.JSONDecodeError:
                    # 跳过损坏的记录
                    continue
            return results
    
    def query_by_filename(self, filename: str) -> List[Dict[str, Any]]:
        """根据文件名查询"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, filename, parse_time, summary_json, archive_info_json
                FROM parse_results 
                WHERE filename LIKE ? 
                ORDER BY id DESC
            ''', (f"%{filename}%",))
            
            rows = cursor.fetchall()
            results = []
            for row in rows:
                try:
                    summary = json.loads(row['summary_json'])
                    archive_info = json.loads(row['archive_info_json'])
                    results.append({
                        'id': row['id'],
                        'filename': row['filename'],
                        'parse_time': row['parse_time'],
                        'summary': summary,
                        'archive_info': archive_info
                    })
                except json.JSONDecodeError:
                    continue
            return results
    
    def get_result_by_id(self, result_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取单个结果"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, filename, parse_time, summary_json, archive_info_json
                FROM parse_results 
                WHERE id = ?
            ''', (result_id,))
            
            row = cursor.fetchone()
            if row:
                try:
                    summary = json.loads(row['summary_json'])
                    archive_info = json.loads(row['archive_info_json'])
                    return {
                        'id': row['id'],
                        'filename': row['filename'],
                        'parse_time': row['parse_time'],
                        'summary': summary,
                        'archive_info': archive_info
                    }
                except json.JSONDecodeError:
                    return None
            return None
    
    def delete_result(self, result_id: int) -> bool:
        """删除指定ID的记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM parse_results WHERE id = ?', (result_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def clear_database(self) -> int:
        """清空数据库，返回删除的记录数"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM parse_results')
            count = cursor.fetchone()[0]
            
            cursor.execute('DELETE FROM parse_results')
            conn.commit()
            return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 总记录数
            cursor.execute('SELECT COUNT(*) FROM parse_results')
            total_records = cursor.fetchone()[0]
            
            # 总数据段数
            cursor.execute('''
                SELECT SUM(json_array_length(sections_json)) 
                FROM parse_results
            ''')
            total_sections = cursor.fetchone()[0] or 0
            
            # 总数据表数
            cursor.execute('''
                SELECT SUM(
                    (SELECT COUNT(*) FROM json_each(sections_json) 
                     WHERE json_type(value, '$.tables') = 'array')
                ) FROM parse_results
            ''')
            total_tables = cursor.fetchone()[0] or 0
            
            # 总数据行数（近似值）
            cursor.execute('''
                SELECT SUM(file_size) FROM parse_results
            ''')
            total_file_size = cursor.fetchone()[0] or 0
            
            # 最新记录时间
            cursor.execute('''
                SELECT MAX(parse_time) FROM parse_results
            ''')
            latest_parse_time = cursor.fetchone()[0]
            
            return {
                'total_records': total_records,
                'total_sections': total_sections,
                'total_tables': total_tables,
                'total_file_size': total_file_size,
                'latest_parse_time': latest_parse_time
            }
    
    def get_db_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 数据库版本
            cursor.execute('SELECT version FROM db_version')
            version = cursor.fetchone()
            db_version = version[0] if version else "unknown"
            
            # 数据库文件大小
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            # 表数量
            cursor.execute('''
                SELECT COUNT(*) FROM sqlite_master WHERE type='table'
            ''')
            table_count = cursor.fetchone()[0]
            
            return {
                'version': db_version,
                'size': db_size,
                'table_count': table_count,
                'path': self.db_path
            }


# 兼容性函数（保持向后兼容）
def init_db(db_path: str = None):
    """初始化数据库（兼容性函数）"""
    if db_path is None:
        # 获取exe所在目录的路径（适用于打包后的exe）
        if getattr(sys, 'frozen', False):
            # 打包后的exe
            app_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境
            app_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(app_dir, "eparser.db")
    
    db_manager = DatabaseManager(db_path)
    db_manager.init_db()


def save_result(result: dict, tar_info: dict = None, db_path: str = None):
    """保存结果（兼容性函数）"""
    if db_path is None:
        # 获取exe所在目录的路径（适用于打包后的exe）
        if getattr(sys, 'frozen', False):
            # 打包后的exe
            app_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境
            app_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(app_dir, "eparser.db")
    
    db_manager = DatabaseManager(db_path)
    
    # 构建文件信息
    file_info = {}
    if result.get('filename') and os.path.exists(result['filename']):
        stat = os.stat(result['filename'])
        file_info = {
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    db_manager.save_result(result, file_info)


def query_results(db_path: str = None):
    """查询结果（兼容性函数）"""
    if db_path is None:
        # 获取exe所在目录的路径（适用于打包后的exe）
        if getattr(sys, 'frozen', False):
            # 打包后的exe
            app_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境
            app_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(app_dir, "eparser.db")
    
    db_manager = DatabaseManager(db_path)
    results = db_manager.query_results()
    
    # 转换为旧格式
    old_format_results = []
    for result in results:
        old_format_results.append((
            result['id'],
            result['filename'],
            result['parse_time'],
            result['summary'],
            result.get('archive_info', {})
        ))
    
    return old_format_results


def get_database_manager(db_path: str = None) -> DatabaseManager:
    """获取数据库管理器实例"""
    if db_path is None:
        # 获取exe所在目录的路径（适用于打包后的exe）
        if getattr(sys, 'frozen', False):
            # 打包后的exe
            app_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境
            app_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(app_dir, "eparser.db")
    
    return DatabaseManager(db_path)


if __name__ == "__main__":
    # 测试代码
    import tempfile
    
    # 创建临时数据库进行测试
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # 初始化数据库
        db_manager = DatabaseManager(db_path)
        db_manager.init_db()
        print("✅ 数据库初始化成功")
        
        # 测试保存
        test_result = {
            'filename': 'test.dat',
            'parse_time': '2024-01-01 12:00:00',
            'header': {'System': 'Test', 'Version': '1.0'},
            'sections': [
                {
                    'tag': 'TEST::STATION1',
                    'type': 'TEST',
                    'station': 'STATION1',
                    'date': '2024-01-01',
                    'time': '12:00:00',
                    'tables': [
                        {
                            'header': ['col1', 'col2'],
                            'rows': [{'col1': 'val1', 'col2': 'val2'}],
                            'row_count': 1
                        }
                    ]
                }
            ]
        }
        
        db_manager.save_result(test_result)
        print("✅ 数据保存成功")
        
        # 测试查询
        results = db_manager.query_results()
        print(f"✅ 查询到 {len(results)} 条记录")
        
        # 测试统计
        stats = db_manager.get_statistics()
        print(f"📊 统计信息: {stats}")
        
        # 测试数据库信息
        db_info = db_manager.get_db_info()
        print(f"📁 数据库信息: {db_info}")
        
    finally:
        # 清理临时文件
        if os.path.exists(db_path):
            os.unlink(db_path)