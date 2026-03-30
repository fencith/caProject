from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import re
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from efile_parser_optimized import parse_efile, generate_html_report, EFileParserError
from db_utils_optimized import get_database_manager, DatabaseError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # 生产环境请使用更安全的密钥
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 限制
app.config['ALLOWED_EXTENSIONS'] = {'.dat', '.tar.gz', '.tgz', '.tar', '.lbx'}

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 获取数据库管理器
db_manager = get_database_manager()


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           os.path.splitext(filename)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """主页"""
    try:
        stats = db_manager.get_statistics()
        db_info = db_manager.get_db_info()
        
        return render_template('index.html', 
                             stats=stats, 
                             db_info=db_info,
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        logger.error(f"主页加载失败: {e}")
        flash("数据库连接失败", "error")
        return render_template('index.html', stats={}, db_info={})


@app.route('/upload', methods=['POST'])
def upload_file():
    """文件上传处理"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式。请上传 .dat, .tar.gz, .tgz, .tar 或 .lbx 文件'}), 400
    
    try:
        # 安全地保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(filepath)
        
        logger.info(f"文件已保存: {filepath}")
        
        # 解析文件
        result = parse_efile(filepath)
        
        # 保存到数据库
        file_info = {
            'size': os.path.getsize(filepath),
            'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
        }
        db_manager.save_result(result, file_info)
        
        # 生成HTML报告
        html_report = generate_html_report(result)
        
        # 保存报告文件
        report_filename = safe_filename.replace(os.path.splitext(safe_filename)[1], '_report.html')
        report_filepath = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
        
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        logger.info(f"报告已生成: {report_filepath}")
        
        return jsonify({
            'success': True,
            'message': '文件解析成功',
            'report_url': url_for('download_report', filename=report_filename),
            'data': {
                'filename': filename,
                'parse_time': result.get('parse_time'),
                'sections_count': len(result.get('sections', [])),
                'total_tables': sum(len(s['tables']) for s in result.get('sections', [])),
                'total_rows': sum(sum(t['row_count'] for t in s['tables']) for s in result.get('sections', []))
            }
        })
        
    except EFileParserError as e:
        logger.error(f"文件解析失败: {e}")
        return jsonify({'error': f'文件解析失败: {str(e)}'}), 400
    except DatabaseError as e:
        logger.error(f"数据库保存失败: {e}")
        return jsonify({'error': f'数据库保存失败: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"上传处理失败: {e}")
        return jsonify({'error': f'处理失败: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_report(filename):
    """下载报告文件"""
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], filename),
            as_attachment=False,
            mimetype='text/html'
        )
    except Exception as e:
        logger.error(f"下载报告失败: {e}")
        return jsonify({'error': '报告文件不存在或下载失败'}), 404


@app.route('/api/stats')
def api_stats():
    """API: 获取统计信息"""
    try:
        stats = db_manager.get_statistics()
        db_info = db_manager.get_db_info()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'db_info': db_info
        })
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/results')
def api_results():
    """API: 获取解析结果列表"""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        results = db_manager.query_results(limit=limit, offset=offset)
        
        # 转换为API格式
        api_results = []
        for result in results:
            summary = result['summary']
            api_results.append({
                'id': result['id'],
                'filename': result['filename'],
                'parse_time': result['parse_time'],
                'sections_count': len(summary.get('sections', [])),
                'total_tables': sum(len(s['tables']) for s in summary.get('sections', [])),
                'total_rows': sum(sum(t['row_count'] for t in s['tables']) for s in summary.get('sections', [])),
                'archive_info': result.get('archive_info', {})
            })
        
        return jsonify({
            'success': True,
            'results': api_results,
            'total': len(api_results)
        })
    except Exception as e:
        logger.error(f"获取结果列表失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/result/<int:result_id>')
def api_result_detail(result_id):
    """API: 获取单个结果详情"""
    try:
        result = db_manager.get_result_by_id(result_id)
        if result:
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            return jsonify({'error': '结果不存在'}), 404
    except Exception as e:
        logger.error(f"获取结果详情失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete/<int:result_id>', methods=['DELETE'])
def api_delete_result(result_id):
    """API: 删除单个结果"""
    try:
        success = db_manager.delete_result(result_id)
        if success:
            return jsonify({'success': True, 'message': '删除成功'})
        else:
            return jsonify({'error': '结果不存在或删除失败'}), 404
    except Exception as e:
        logger.error(f"删除结果失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def api_clear_database():
    """API: 清空数据库"""
    try:
        count = db_manager.clear_database()
        return jsonify({
            'success': True,
            'message': f'已清空数据库，删除了 {count} 条记录'
        })
    except Exception as e:
        logger.error(f"清空数据库失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({'error': '文件过大，最大支持 16MB'}), 413


@app.errorhandler(500)
def internal_error(e):
    """内部错误处理"""
    logger.error(f"内部错误: {e}")
    return jsonify({'error': '服务器内部错误'}), 500


@app.template_filter('filesizeformat')
def filesizeformat(value):
    """文件大小格式化过滤器"""
    if value is None:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if value < 1024.0:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} PB"


@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    """日期时间格式化过滤器"""
    if value is None:
        return ""
    try:
        dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return dt.strftime(format)
    except:
        return value


if __name__ == '__main__':
    # 初始化数据库
    try:
        db_manager.init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
    
    # 启动应用
    app.run(debug=True, port=5000, host='0.0.0.0')