# backend/transcribe.py - 核心转录代码
import os
import tempfile
import numpy as np
from basic_pitch.inference import predict
import pretty_midi

class MusicTranscriber:
    """音乐转录器类"""
    
    def __init__(self):
        print("🎹 音乐转录器初始化...")
        # 这里可以加载模型或初始化资源
    
    def transcribe_audio(self, audio_path, output_midi=None, upload_folder=None):
        """
        转录音频文件为MIDI
        
        参数:
            audio_path: 音频文件路径
            output_midi: 输出MIDI路径（可选）
            upload_folder: 上传文件夹路径（可选，用于移动文件）
        """
        print(f"开始转录: {audio_path}")
        
        try:
            # 1. 使用 basic-pitch 转录
            print("正在分析音频...")
            model_output, midi_data, note_events = predict(
                audio_path,
                onset_threshold=0.5,
                frame_threshold=0.3,
                minimum_note_length=0.058
            )
            
            # 2. 保存MIDI文件
            if output_midi is None:
                # 生成临时文件
                temp_dir = tempfile.gettempdir()
                output_midi = os.path.join(temp_dir, f"transcribed_{os.path.basename(audio_path)}.mid")
            
            midi_data.write(output_midi)
            
            # 3. 分析结果
            notes_count = len(midi_data.instruments[0].notes) if midi_data.instruments else 0
            
            # 如果指定了上传文件夹，移动文件
            final_midi_path = output_midi
            if upload_folder:
                import shutil
                # 只取文件名，不要路径
                filename = os.path.basename(output_midi)
                target_path = os.path.join(upload_folder, filename)
                shutil.move(output_midi, target_path)
                final_midi_path = target_path
            
            result = {
                'success': True,
                'midi_path': final_midi_path,
                'notes_count': notes_count,
                'message': '转录成功'
            }
            
            return result

        except Exception as e:
            print(f"❌ 转录失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_audio_info(self, audio_path):
        """获取音频文件信息"""
        try:
            import librosa
            duration = librosa.get_duration(path=audio_path)
            return {
                'duration': duration,
                'size': os.path.getsize(audio_path)
            }
        except:
            return {'duration': 0, 'size': 0}

# 测试代码（运行这个文件单独测试）
if __name__ == "__main__":
    transcriber = MusicTranscriber()
    
    # 测试转录
    test_audio = "test_piano.mp3"  # 你需要有一个测试文件
    if os.path.exists(test_audio):
        result = transcriber.transcribe_audio(test_audio, "output.mid")
        print(result)
    else:
        print(f"测试文件不存在: {test_audio}")