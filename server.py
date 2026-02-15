# backend/server.py - Flask API服务器
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import uuid
import subprocess
from werkzeug.utils import secure_filename
from transcribe import MusicTranscriber  # 导入我们的转录类
import json
import pretty_midi
try:
    from music21 import converter, stream, note, chord, meter, key
except ImportError:
    print("警告: music21 库未安装，将使用简化版乐谱解析")
    converter = None

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

def check_musescore_installed():
    """检查MuseScore是否安装"""
    try:
        # 尝试运行 musescore 或 mscore
        for cmd in ['musescore', 'mscore', '/usr/bin/musescore', '/usr/bin/mscore']:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print(f"✅ MuseScore 找到: {cmd}")
                    return cmd
            except:
                continue
        print("❌ MuseScore 未找到")
        return None
    except Exception as e:
        print(f"检查MuseScore时出错: {e}")
        return None

# 在应用启动时检查
MUSESCORE_PATH = check_musescore_installed()

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """首页，检查服务是否正常"""
    print("收到根路径请求")  # Railway 日志能看到
    endpoints = {
        '/': '服务状态',
        '/health': '健康检查',
        '/api/transcribe': '音频转录',
        '/api/download/<filename>': '下载文件'
    }
    
    # 如果MuseScore可用，添加PDF相关接口
    if MUSESCORE_PATH:
        endpoints.update({
            '/api/generate-pdf': '生成PDF乐谱',
            '/api/convert-to-pdf/<midi_filename>': '转换MIDI为PDF',
            '/api/check-pdf-support': '检查PDF支持'
        })
    
    return jsonify({
        'status': 'running',
        'service': 'Music Transcription API',
        'version': '1.0.0',
        'endpoints': endpoints
    })

@app.route('/health', methods=['GET'])
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
        result = transcriber.transcribe_audio(filepath, upload_folder=app.config['UPLOAD_FOLDER'])
        
        if result['success']:
            # 生成下载文件名（现在文件已经在uploads目录）
            download_filename = os.path.basename(result['midi_path'])
            
            response_data = {
                'success': True,
                'message': '音频转录成功',
                'filename': download_filename,
                'real_path': result['midi_path'],
                'notes_count': result['notes_count'],
                'original_filename': filename,
                'file_size': file_size
            }
            
            # 如果MuseScore可用，添加PDF转换信息
            if MUSESCORE_PATH:
                response_data['pdf_supported'] = True
                response_data['pdf_conversion_url'] = f'/api/convert-to-pdf/{download_filename}'
            
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

@app.route('/api/score-data/<filename>', methods=['GET'])
def get_score_data(filename):
    """获取乐谱渲染数据（VexFlow格式）"""
    try:
        safe_filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'MIDI文件不存在'
            }), 404
        
        # 解析MIDI文件生成乐谱数据
        score_data = parse_midi_to_vexflow(filepath)
        
        return jsonify({
            'success': True,
            'score_data': score_data,
            'filename': safe_filename
        })
        
    except Exception as e:
        print(f'乐谱数据生成失败: {e}')
        return jsonify({
            'success': False,
            'error': f'乐谱数据生成失败: {str(e)}'
        }), 500

def parse_midi_to_vexflow(midi_path):
    """将MIDI文件解析为VexFlow格式的乐谱数据"""
    try:
        # 使用pretty_midi解析MIDI
        midi_data = pretty_midi.PrettyMIDI(midi_path)
        
        # 提取乐谱信息
        score_info = {
            'title': '转录乐谱',
            'composer': 'AI转录',
            'time_signature': '4/4',
            'key_signature': 'C',
            'tempo': 120
        }
        
        # 提取音符数据
        notes_data = []
        for instrument in midi_data.instruments:
            for note_obj in instrument.notes:
                # 使用安全的音符名称转换
                pitch_name = get_note_name(note_obj.pitch)
                notes_data.append({
                    'pitch': pitch_name,
                    'start_time': note_obj.start,
                    'end_time': note_obj.end,
                    'velocity': note_obj.velocity,
                    'duration': note_obj.end - note_obj.start
                })
        
        # 转换为VexFlow格式
        vexflow_data = {
            'staves': [{
                'clef': 'treble',
                'key': score_info['key_signature'],
                'time': score_info['time_signature'],
                'notes': convert_notes_to_vexflow(notes_data)
            }]
        }
        
        return vexflow_data
        
    except Exception as e:
        print(f'MIDI解析错误: {e}')
        # 返回简化数据作为备选
        return get_fallback_score_data()

def get_note_name(note_number):
    """将音符编号转换为音符名称"""
    # 简单的音符名称映射
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = note_number // 12 - 1
    note_index = note_number % 12
    return f"{note_names[note_index]}/{octave}"

def convert_notes_to_vexflow(notes_data):
    """将音符数据转换为VexFlow格式"""
    vexflow_notes = []
    
    for note_obj in notes_data[:20]:  # 限制音符数量避免数据过大
        pitch = note_obj['pitch'].replace('#', '#')
        duration = get_note_duration(note_obj['duration'])
        
        vexflow_notes.append({
            'keys': [pitch],
            'duration': duration,
            'stem_direction': 1
        })
    
    return vexflow_notes

def get_note_duration(duration):
    """根据时长确定音符时值"""
    if duration >= 1.0:
        return 'w'  # 全音符
    elif duration >= 0.5:
        return 'h'  # 二分音符
    elif duration >= 0.25:
        return 'q'  # 四分音符
    elif duration >= 0.125:
        return '8'  # 八分音符
    else:
        return '16'  # 十六分音符

def get_fallback_score_data():
    """返回备用的简单乐谱数据"""
    return {
        'staves': [{
            'clef': 'treble',
            'key': 'C',
            'time': '4/4',
            'notes': [
                {'keys': ['c/4'], 'duration': 'q', 'stem_direction': 1},
                {'keys': ['d/4'], 'duration': 'q', 'stem_direction': 1},
                {'keys': ['e/4'], 'duration': 'q', 'stem_direction': 1},
                {'keys': ['f/4'], 'duration': 'q', 'stem_direction': 1}
            ]
        }]
    }

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """将MIDI转换为PDF乐谱"""
    try:
        print("\n=== 开始生成PDF ===")
        
        # 检查MuseScore是否可用
        if not MUSESCORE_PATH:
            return jsonify({
                'success': False,
                'error': 'PDF生成功能不可用（MuseScore未安装）',
                'available': False
            }), 503
        
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400
        
        # 保存上传的MIDI文件
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        
        # 确保是.mid文件
        if not original_filename.lower().endswith('.mid'):
            return jsonify({'success': False, 'error': '请上传MIDI文件'}), 400
        
        # 保存文件
        midi_filename = f"input_{unique_id}.mid"
        midi_path = os.path.join(app.config['UPLOAD_FOLDER'], midi_filename)
        file.save(midi_path)
        
        print(f"MIDI文件保存到: {midi_path}")
        print(f"文件大小: {os.path.getsize(midi_path)} bytes")
        
        # 生成PDF文件名
        pdf_filename = f"score_{unique_id}.pdf"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        
        print(f"开始转换: {midi_path} -> {pdf_path}")
        print(f"使用MuseScore路径: {MUSESCORE_PATH}")
        
        # 执行转换命令
        cmd = [
            MUSESCORE_PATH,
            '-o', pdf_path,  # 输出PDF
            midi_path        # 输入MIDI
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30秒超时
        )
        
        if result.returncode != 0:
            print(f"MuseScore错误: {result.stderr}")
            return jsonify({
                'success': False,
                'error': f'转换失败: {result.stderr[:100]}',
                'details': result.stderr
            }), 500
        
        # 检查PDF是否生成
        if not os.path.exists(pdf_path):
            return jsonify({'success': False, 'error': 'PDF文件未生成'}), 500
        
        pdf_size = os.path.getsize(pdf_path)
        print(f"✅ PDF生成成功: {pdf_path} ({pdf_size} bytes)")
        
        # 返回PDF文件
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"乐谱_{unique_id}.pdf",
            mimetype='application/pdf'
        )
        
    except subprocess.TimeoutExpired:
        print("❌ PDF转换超时")
        return jsonify({'success': False, 'error': '转换超时，请稍后重试'}), 500
    except Exception as e:
        print(f"❌ PDF生成错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

@app.route('/api/convert-to-pdf/<midi_filename>', methods=['GET'])
def convert_existing_to_pdf(midi_filename):
    """将已存在的MIDI文件转换为PDF"""
    try:
        print(f"\n=== 转换已有MIDI到PDF: {midi_filename} ===")
        
        if not MUSESCORE_PATH:
            return jsonify({
                'success': False,
                'error': 'PDF功能不可用'
            }), 503
        
        # 安全处理文件名
        safe_filename = secure_filename(midi_filename)
        midi_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        if not os.path.exists(midi_path):
            return jsonify({'success': False, 'error': 'MIDI文件不存在'}), 404
        
        # 生成PDF文件名
        base_name = os.path.splitext(safe_filename)[0]
        pdf_filename = f"{base_name}.pdf"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        
        print(f"转换: {midi_path} -> {pdf_path}")
        
        # 执行转换
        cmd = [MUSESCORE_PATH, '-o', pdf_path, midi_path]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': '转换失败'
            }), 500
        
        # 返回PDF下载信息
        return jsonify({
            'success': True,
            'message': 'PDF生成成功',
            'pdf_filename': pdf_filename,
            'download_url': f'/api/download/{pdf_filename}',
            'midi_original': safe_filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/check-pdf-support', methods=['GET'])
def check_pdf_support():
    """检查PDF生成功能是否可用"""
    return jsonify({
        'success': True,
        'pdf_supported': MUSESCORE_PATH is not None,
        'musescore_path': MUSESCORE_PATH,
        'message': 'PDF生成功能已启用' if MUSESCORE_PATH else 'PDF生成功能不可用'
    })

if __name__ == '__main__':
    print("🚀 启动音乐转录API服务器...")
    # 获取 Railway 提供的端口
    port = int(os.environ.get('PORT', 5000))
    print(f"监听端口: {port}")
    print(f"Railway 域名: https://music-transcribe-api-production.up.railway.app")
    
    # 打印PDF支持状态
    if MUSESCORE_PATH:
        print("✅ PDF乐谱生成功能已启用")
    else:
        print("⚠️  PDF乐谱生成功能不可用（MuseScore未安装）")
    
    app.run(host='0.0.0.0', port=port, debug=False)