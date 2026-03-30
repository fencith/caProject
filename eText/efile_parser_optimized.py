import re
from datetime import datetime
import tarfile as _tarfile
import zipfile as _zipfile
import tempfile as _tempfile
import os as _os
import shutil as _shutil
from typing import Dict, List, Any, Optional, Tuple, Generator
from contextlib import contextmanager


class EFileParserError(Exception):
    """E文件解析错误异常"""
    pass


class Constants:
    """解析器常量定义"""
    SUPPORTED_ENCODINGS = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'utf-16']
    HEADER_PATTERN = r'<!(.*?)!>'
    SECTION_PATTERN = r'<([A-Z]+::[^\s]+)\s+Date=\'([^\']+)\'\s+Time=\'([^\']+)\'>(.*?)</\1>'
    TABLE_PATTERN = r'@\s+(.*?)\n((?:#.*?\n)*)'
    TAR_EXTENSIONS = ['.tar.gz', '.tgz', '.tar']
    LBX_EXTENSION = '.lbx'
    DAT_EXTENSION = '.dat'


@contextmanager
def temporary_directory():
    """临时目录上下文管理器"""
    tmpdir = _tempfile.mkdtemp()
    try:
        yield tmpdir
    finally:
        _shutil.rmtree(tmpdir, ignore_errors=True)


def detect_file_encoding(filepath: str) -> Optional[str]:
    """检测文件编码"""
    for encoding in Constants.SUPPORTED_ENCODINGS:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                f.read(1024)  # 只读取前1024字节进行检测
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None


def read_file_content(filepath: str, encoding: Optional[str] = None) -> str:
    """读取文件内容"""
    if encoding is None:
        encoding = detect_file_encoding(filepath)
        if encoding is None:
            raise EFileParserError(f"无法读取文件 {filepath}: 不支持的文件编码")
    
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        raise EFileParserError(f"读取文件 {filepath} 时出错: {str(e)}")


def parse_header(content: str) -> Dict[str, str]:
    """解析文件头信息"""
    header_match = re.search(Constants.HEADER_PATTERN, content)
    if not header_match:
        return {}
    
    header_str = header_match.group(1)
    header_parts = re.findall(r'(\w+)=([\d.]+|UTF-8|GBK|GB2312|GB18030)', header_str)
    return dict(header_parts)


def parse_table_data(table_header_str: str, table_data_str: str) -> Dict[str, Any]:
    """解析数据表"""
    columns = [col.strip() for col in re.split(r'\t+', table_header_str) if col.strip()]
    rows = []
    
    row_lines = [line.strip() for line in table_data_str.split('\n') 
                 if line.strip() and line.startswith('#')]
    
    for row_line in row_lines:
        values_str = row_line[1:].strip()
        values = [val.strip() for val in re.split(r'\t+', values_str)]
        rows.append(dict(zip(columns, values)))
    
    return {
        'header': columns,
        'rows': rows,
        'row_count': len(rows)
    }


def parse_section_data(section_content: str) -> List[Dict[str, Any]]:
    """解析数据段中的数据表"""
    tables = []
    table_matches = re.findall(Constants.TABLE_PATTERN, section_content, re.DOTALL)
    
    for table_header_str, table_data_str in table_matches:
        table = parse_table_data(table_header_str, table_data_str)
        if table['header']:  # 只添加有表头的表
            tables.append(table)
    
    return tables


def parse_section(section_tag: str, date_str: str, time_str: str, section_content: str) -> Dict[str, Any]:
    """解析单个数据段"""
    section_parts = section_tag.split('::')
    section_type = section_parts[0]
    station = section_parts[1] if len(section_parts) > 1 else ''
    
    return {
        'tag': section_tag,
        'type': section_type,
        'station': station,
        'date': date_str,
        'time': time_str,
        'tables': parse_section_data(section_content)
    }


def parse_single_file(filepath: str) -> Dict[str, Any]:
    """解析单个.dat文件"""
    content = read_file_content(filepath)
    
    result = {
        'filename': filepath,
        'parse_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'header': parse_header(content),
        'sections': []
    }
    
    section_matches = re.findall(Constants.SECTION_PATTERN, content, re.DOTALL)
    
    for section_tag, date_str, time_str, section_content in section_matches:
        section = parse_section(section_tag, date_str, time_str, section_content)
        if section['tables']:  # 只添加有数据表的段
            result['sections'].append(section)
    
    return result


def parse_tar_archive(filename: str) -> Dict[str, Any]:
    """解析tar.gz压缩包"""
    merged = {
        'filename': filename,
        'parse_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'header': {},
        'sections': [],
        'archive_info': {
            'archive_name': _os.path.basename(filename),
            'archive_type': 'tar',
            'dat_count': 0,
            'dat_files': []
        }
    }
    
    if not _tarfile.is_tarfile(filename):
        raise EFileParserError(f"{filename} 不是有效的tar文件")
    
    with temporary_directory() as tmpdir:
        with _tarfile.open(filename, 'r:*') as tar:
            tar.extractall(tmpdir)
            
            # 递归查找所有.dat文件
            dat_paths = []
            for root, dirs, files in _os.walk(tmpdir):
                for f in files:
                    if f.lower().endswith(Constants.DAT_EXTENSION):
                        dat_paths.append(_os.path.join(root, f))
            
            dat_paths.sort()
            merged['archive_info']['dat_count'] = len(dat_paths)
            merged['archive_info']['dat_files'] = [os.path.relpath(p, tmpdir) for p in dat_paths]
            
            for dp in dat_paths:
                try:
                    sub = parse_single_file(dp)
                    if sub.get('header') and not merged['header']:
                        merged['header'] = sub['header']
                    merged['sections'].extend(sub.get('sections', []))
                except Exception as e:
                    # 记录错误但继续处理其他文件
                    print(f"警告: 解析文件 {dp} 时出错: {str(e)}")
    
    return merged


def parse_lbx_archive(filename: str) -> Dict[str, Any]:
    """解析.lbx压缩包（ZIP格式）"""
    merged = {
        'filename': filename,
        'parse_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'header': {},
        'sections': [],
        'archive_info': {
            'archive_name': _os.path.basename(filename),
            'archive_type': 'lbx',
            'dat_count': 0,
            'dat_files': []
        }
    }
    
    try:
        with _zipfile.ZipFile(filename, 'r') as zf:
            with temporary_directory() as tmpdir:
                try:
                    zf.extractall(tmpdir)
                except RuntimeError as e:
                    if "password required" in str(e):
                        raise EFileParserError(f"LBX文件 {filename} 需要密码才能解压")
                    else:
                        raise
                
                # 递归查找所有.dat文件
                dat_paths = []
                for root, dirs, files in _os.walk(tmpdir):
                    for f in files:
                        if f.lower().endswith(Constants.DAT_EXTENSION):
                            dat_paths.append(_os.path.join(root, f))
                
                dat_paths.sort()
                merged['archive_info']['dat_count'] = len(dat_paths)
                merged['archive_info']['dat_files'] = [os.path.relpath(p, tmpdir) for p in dat_paths]
                
                for dp in dat_paths:
                    try:
                        sub = parse_single_file(dp)
                        if sub.get('header') and not merged['header']:
                            merged['header'] = sub['header']
                        merged['sections'].extend(sub.get('sections', []))
                    except Exception as e:
                        # 记录错误但继续处理其他文件
                        print(f"警告: 解析文件 {dp} 时出错: {str(e)}")
                        
    except _zipfile.BadZipFile:
        raise EFileParserError(f"无法解压LBX文件 {filename}: 不是有效的ZIP文件")
    
    return merged


def parse_efile(filename: str) -> Dict[str, Any]:
    """
    解析E文件
    
    支持的文件格式:
    - 单个.dat文件
    - tar.gz压缩包
    - .lbx压缩包（ZIP格式）
    
    Args:
        filename: 文件路径
        
    Returns:
        解析结果字典
        
    Raises:
        EFileParserError: 解析错误时抛出
    """
    if not _os.path.exists(filename):
        raise EFileParserError(f"文件不存在: {filename}")
    
    file_ext = _os.path.splitext(filename)[1].lower()
    
    if any(filename.lower().endswith(ext) for ext in Constants.TAR_EXTENSIONS):
        return parse_tar_archive(filename)
    elif file_ext == Constants.LBX_EXTENSION:
        return parse_lbx_archive(filename)
    else:
        # 默认按单个.dat文件处理
        return parse_single_file(filename)


def generate_html_report(data: Dict[str, Any]) -> str:
    """生成HTML报告"""
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E文件解析报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: "Microsoft YaHei", Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header .meta {{ font-size: 14px; opacity: 0.9; }}
        .section {{ margin: 20px; padding: 20px; border: 1px solid #e0e0e0; border-radius: 6px; }}
        .section-title {{ font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; }}
        .info-table th, .info-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #e0e0e0; }}
        .info-table th {{ background: #f8f9fa; font-weight: bold; color: #555; }}
        .data-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; overflow-x: auto; }}
        .data-table th, .data-table td {{ padding: 8px; text-align: left; border: 1px solid #ddd; font-size: 12px; }}
        .data-table th {{ background: #667eea; color: white; white-space: nowrap; }}
        .data-table tr:nth-child(even) {{ background: #f9f9f9; }}
        .data-table tr:hover {{ background: #e3f2fd; }}
        .tag {{ display: inline-block; padding: 4px 8px; background: #e3f2fd; color: #1976d2; border-radius: 4px; font-size: 12px; margin-right: 5px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .summary-card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #667eea; }}
        .summary-card .label {{ font-size: 12px; color: #666; margin-bottom: 5px; }}
        .summary-card .value {{ font-size: 20px; font-weight: bold; color: #333; }}
        .archive-info {{ background: #e8f5e9; padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
        .archive-info h3 {{ color: #2e7d32; margin-bottom: 10px; }}
        .file-list {{ max-height: 200px; overflow-y: auto; border: 1px solid #c8e6c9; border-radius: 4px; padding: 10px; }}
        .file-item {{ font-size: 12px; color: #388e3c; margin-bottom: 5px; padding: 2px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 E文件解析报告</h1>
            <div class="meta">
                <p>文件名: {filename}</p>
                <p>解析时间: {parse_time}</p>
            </div>
        </div>
    '''.format(filename=data['filename'], parse_time=data['parse_time'])

    # 添加压缩包信息（如果有）
    if 'archive_info' in data:
        archive_info = data['archive_info']
        html += '''        <div class="archive-info">
            <h3>📦 压缩包信息</h3>
            <p><strong>压缩包类型:</strong> {archive_type}</p>
            <p><strong>包含.dat文件数:</strong> {dat_count}</p>
            <div class="file-list">
                {file_list}
            </div>
        </div>
    '''.format(
            archive_type=archive_info['archive_type'],
            dat_count=archive_info['dat_count'],
            file_list=''.join(f'<div class="file-item">• {f}</div>' for f in archive_info['dat_files'])
        )

    html += '''        <div class="section">
            <div class="section-title">📊 文件概览</div>
            <div class="summary">
                <div class="summary-card">
                    <div class="label">数据段数量</div>
                    <div class="value">{}</div>
                </div>
                <div class="summary-card">
                    <div class="label">总数据表数量</div>
                    <div class="value">{}</div>
                </div>
                <div class="summary-card">
                    <div class="label">总数据行数</div>
                    <div class="value">{}</div>
                </div>
            </div>
            <table class="info-table">
                <tr>
                    <th>参数</th>
                    <th>值</th>
                </tr>'''.format(
        len(data['sections']),
        sum(len(s['tables']) for s in data['sections']),
        sum(sum(t['row_count'] for t in s['tables']) for s in data['sections'])
    )

    for key, value in data['header'].items():
        html += '''                <tr>
                    <td>{}</td>
                    <td>{}</td>
                </tr>'''.format(key, value)

    html += '''            </table>
        </div>
    '''

    for idx, section in enumerate(data['sections'], 1):
        html += '''        <div class="section">
            <div class="section-title">
                📁 数据段 {idx}: {type}
                <span class="tag">{tag}</span>
            </div>
            <table class="info-table">
                <tr>
                    <th>参数</th>
                    <th>值</th>
                </tr>
                <tr>
                    <td>场站</td>
                    <td>{station}</td>
                </tr>
                <tr>
                    <td>日期</td>
                    <td>{date}</td>
                </tr>
                <tr>
                    <td>时间</td>
                    <td>{time}</td>
                </tr>
                <tr>
                    <td>数据表数量</td>
                    <td>{table_count}</td>
                </tr>
            </table>
        </div>
    '''.format(
        idx=idx,
        type=section['type'],
        tag=section['tag'],
        station=section['station'],
        date=section['date'],
        time=section['time'],
        table_count=len(section['tables'])
    )

        for table_idx, table in enumerate(section['tables'], 1):
            html += '''            <div style="margin-top: 20px;">
                <h3 style="margin-bottom: 10px; color: #667eea;">数据表 {table_idx} ({row_count} 行)</h3>
                <div style="overflow-x: auto;">
                    <table class="data-table">
                        <thead>
                            <tr>'''.format(table_idx=table_idx, row_count=table['row_count'])

            for col in table['header']:
                html += '                                <th>{}</th>'.format(col)

            html += '''                            </tr>
                        </thead>
                        <tbody>'''

            for row in table['rows']:
                html += '                            <tr>'
                for col in table['header']:
                    html += '                                <td>{}</td>'.format(row.get(col, ""))
                html += '                            </tr>'

            html += '''                        </tbody>
                    </table>
                </div>
            </div>
    '''

        html += '        </div>\n'

    html += '''    </div>
</body>
</html>'''

    return html


def save_report_to_file(data: Dict[str, Any], output_path: str):
    """将报告保存到文件"""
    html_content = generate_html_report(data)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def get_file_info(filepath: str) -> Dict[str, Any]:
    """获取文件信息"""
    if not _os.path.exists(filepath):
        return {}
    
    stat = _os.stat(filepath)
    return {
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
        'extension': _os.path.splitext(filepath)[1].lower()
    }


def validate_result(result: Dict[str, Any]) -> bool:
    """验证解析结果"""
    if not result or 'sections' not in result:
        return False
    
    # 检查是否有有效的数据段
    valid_sections = [s for s in result['sections'] if s.get('tables')]
    return len(valid_sections) > 0


if __name__ == "__main__":
    # 测试代码
    import sys
    if len(sys.argv) > 1:
        try:
            result = parse_efile(sys.argv[1])
            print(f"解析成功: {len(result['sections'])} 个数据段")
            print(f"总数据表数: {sum(len(s['tables']) for s in result['sections'])}")
            print(f"总数据行数: {sum(sum(t['row_count'] for t in s['tables']) for s in result['sections'])}")
        except EFileParserError as e:
            print(f"解析失败: {e}")
        except Exception as e:
            print(f"未知错误: {e}")
    else:
        print("用法: python efile_parser_optimized.py <文件路径>")