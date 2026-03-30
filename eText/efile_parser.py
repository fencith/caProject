import re
from datetime import datetime
import tarfile as _tarfile
import zipfile as _zipfile
import tempfile as _tempfile
import os as _os
import shutil as _shutil


def parse_efile(filename):
    # Tar archive support (tar.gz, tgz)
    if _tarfile.is_tarfile(filename):
        merged = {
            'filename': filename,
            'parse_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'header': {},
            'sections': [],
            'tar_info': {'tar_name': _os.path.basename(filename), 'dat_count': 0}
        }
        with _tarfile.open(filename, 'r:*') as tar:
            tmpdir = _tempfile.mkdtemp()
            tar.extractall(tmpdir)
            dat_paths = []
            for root, dirs, files in _os.walk(tmpdir):
                for f in files:
                    if f.lower().endswith('.dat'):
                        dat_paths.append(_os.path.join(root, f))
            dat_paths.sort()
            for dp in dat_paths:
                sub = parse_efile(dp)
                if sub.get('header') and not merged['header']:
                    merged['header'] = sub['header']
                merged['sections'].extend(sub.get('sections', []))
            merged['tar_info']['dat_count'] = len(dat_paths)
        _shutil.rmtree(tmpdir)
        return merged

    # LBX archive support (.lbx files are ZIP compressed)
    if filename.lower().endswith('.lbx'):
        merged = {
            'filename': filename,
            'parse_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'header': {},
            'sections': [],
            'lbx_info': {'lbx_name': _os.path.basename(filename), 'dat_count': 0}
        }
        try:
            with _zipfile.ZipFile(filename, 'r') as zf:
                tmpdir = _tempfile.mkdtemp()
                # 尝试解压，如果需要密码则跳过
                try:
                    zf.extractall(tmpdir)
                except RuntimeError as e:
                    if "password required" in str(e):
                        raise ValueError(f"LBX文件 {filename} 需要密码才能解压")
                    else:
                        raise
                dat_paths = []
                for root, dirs, files in _os.walk(tmpdir):
                    for f in files:
                        if f.lower().endswith('.dat'):
                            dat_paths.append(_os.path.join(root, f))
                dat_paths.sort()
                for dp in dat_paths:
                    sub = parse_efile(dp)
                    if sub.get('header') and not merged['header']:
                        merged['header'] = sub['header']
                    merged['sections'].extend(sub.get('sections', []))
                merged['lbx_info']['dat_count'] = len(dat_paths)
        except _zipfile.BadZipFile:
            raise ValueError(f"无法解压LBX文件 {filename}: 不是有效的ZIP文件")
        finally:
            if 'tmpdir' in locals():
                _shutil.rmtree(tmpdir)
        return merged

    # Fallback to single file parsing
    # 尝试检测文件编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'utf-16']
    content = None

    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if content is None:
        raise ValueError(f"无法读取文件 {filename}: 不支持的文件编码")

    result = {
        'filename': filename,
        'parse_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'header': {},
        'sections': []
    }

    header_match = re.search(r'<!(.*?)!>', content)
    if header_match:
        header_str = header_match.group(1)
        header_parts = re.findall(r'(\w+)=([\d.]+|UTF-8|GBK|GB2312|GB18030)', header_str)
        for key, value in header_parts:
            result['header'][key] = value
    
    section_pattern = r'<([A-Z]+::[^\s]+)\s+Date=\'([^\']+)\'\s+Time=\'([^\']+)\'>(.*?)</\1>'
    sections = re.findall(section_pattern, content, re.DOTALL)
    
    for section_tag, date_str, time_str, section_content in sections:
        section = {
            'tag': section_tag,
            'type': section_tag.split('::')[0],
            'station': section_tag.split('::')[1] if '::' in section_tag else '',
            'date': date_str,
            'time': time_str,
            'tables': []
        }
        table_pattern = r'@\s+(.*?)\n((?:#.*?\n)*)'
        tables = re.findall(table_pattern, section_content, re.DOTALL)
        for table_header_str, table_data_str in tables:
            columns = [col.strip() for col in re.split(r'\t+', table_header_str) if col.strip()]
            rows = []
            row_lines = [line.strip() for line in table_data_str.split('\n') if line.strip() and line.startswith('#')]
            for row_line in row_lines:
                values_str = row_line[1:].strip()
                values = [val.strip() for val in re.split(r'\t+', values_str)]
                rows.append(dict(zip(columns, values)))
            table = {
                'header': columns,
                'rows': rows,
                'row_count': len(rows)
            }
            section['tables'].append(table)
        result['sections'].append(section)
    
    return result


def generate_html_report(data):
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
