from flask import Flask, render_template, request, jsonify, send_file
import os
import re
from datetime import datetime
from efile_parser import parse_efile, generate_html_report

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not file.filename.endswith('.dat'):
        return jsonify({'error': '请上传.dat格式的E文件'}), 400
    
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    
    try:
        result = parse_efile(filename)
        html_report = generate_html_report(result)
        
        report_filename = filename.replace('.dat', '_report.html')
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        return jsonify({
            'success': True,
            'report_url': f'/download/{os.path.basename(report_filename)}',
            'data': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_report(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=False)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
