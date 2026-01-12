# backend/server.py - Flask API服务器
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import uuid
from werkzeug.utils import secure_filename
from transcribe import MusicTranscriber  # 导入我们的转录类

app = Flask(__name__)
CORS(app)  # 允许小程序跨域访问

# 初始化转录器
transcriber = MusicTranscriber()

# 配置文件上传
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB限制

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """首页，检查服务是否正常"""
    return jsonify({
        'status': 'running',
        'service': 'Music Transcription API',
        'version': '1.0.0',
        'endpoints': {
            '/': '服务状态',
            '/api/health': '健康检查',
            '/api/transcribe': '音频转录',
            '/api/download/<filename>': '下载文件'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': '当前时间'
    })

@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """
    音频转录API接口
    
    接收: multipart/form-data 文件上传
    参数: file (音频文件)
    
    返回: JSON格式的转录结果
    """
    print("收到转录请求...")
    
    # 检查是否有文件
    if 'audio' not in request.files:
        return jsonify({
            'success': False,
            'error': '没有上传文件'
        }), 400
    
    file = request.files['audio']
    
    # 检查文件名
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': '没有选择文件'
        }), 400
    
    # 检查文件类型
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f'不支持的文件类型，请上传 {", ".join(ALLOWED_EXTENSIONS)} 格式'
        }), 400
    
    try:
        # 保存上传的文件
        filename = secure_filename(file.filename)
        # 添加随机字符串防止重名
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        print(f"文件保存到: {filepath}")
        
        # 获取文件信息
        file_size = os.path.getsize(filepath)
        print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
        
        # 转录音频
        print("开始转录处理...")
        result = transcriber.transcribe_audio(filepath)
        
        if result['success']:
            # 生成下载文件名
            download_filename = f"transcribed_{os.path.splitext(filename)[0]}.mid"
            
            response_data = {
                'success': True,
                'message': '音频转录成功',
                'filename': download_filename,
                'real_path': result['midi_path'],  # 服务器上的真实路径
                'notes_count': result['notes_count'],
                'original_filename': filename,
                'file_size': file_size
            }
            
            print(f"转录成功: {response_data}")
            return jsonify(response_data)
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '转录失败')
            }), 500
            
    except Exception as e:
        print(f"API处理错误: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器处理错误: {str(e)}'
        }), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """下载转录后的MIDI文件"""
    try:
        # 安全地获取文件路径
        safe_filename = secure_filename(filename)
        
        # 这里应该从数据库或缓存中获取真实文件路径
        # 简化处理：假设文件在 uploads 目录中
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        if os.path.exists(filepath):
            return send_file(
                filepath,
                as_attachment=True,
                download_name=safe_filename,
                mimetype='audio/midi'
            )
        else:
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 启动音乐转录API服务器...")
    print("访问地址: http://localhost:5000")
    print("API文档: http://localhost:5000/")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)