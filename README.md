# 音乐转录API服务

一个基于Flask的音频转MIDI转录服务，使用basic-pitch库实现高精度的音乐音符识别和MIDI文件生成。

## 功能特性

- 🎵 **音频转MIDI**：支持多种音频格式转换为MIDI格式
- 📤 **文件上传**：通过API上传音频文件进行转录
- 📥 **文件下载**：下载转录后的MIDI文件
- 📊 **转录信息**：返回转录结果的详细信息（音符数量、时长等）
- 🔄 **跨域支持**：支持跨域请求，方便前端集成

## 技术栈

- **后端框架**：Flask
- **核心转录库**：basic-pitch
- **音频处理**：librosa
- **MIDI处理**：pretty_midi
- **依赖管理**：pip
- **部署支持**：Railway

## 安装与运行

### 环境要求

- Python 3.11+
- pip 20.0+

### 安装步骤

1. **克隆或进入项目目录**
   ```bash
   cd backend
   ```

2. **创建虚拟环境（可选但推荐）**
   ```bash
   python -m venv venv
   ```

3. **激活虚拟环境**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

### 运行服务

#### 开发模式
```bash
python server.py
```

服务将在 `http://localhost:5000` 启动

## API接口说明

### 1. 上传音频并转录

**接口地址**：`POST /api/transcribe`

**请求方式**：POST

**请求参数**：
- `file`：音频文件（支持MP3、WAV等格式）

### 2. 下载MIDI文件

**接口地址**：`GET /api/download/<filename>`

**请求方式**：GET

**路径参数**：
- `filename`：MIDI文件名

## 项目结构

```
backend/
├── server.py             # Flask应用主程序
├── transcribe.py         # 音乐转录核心功能
├── railway_config.py     # Railway部署配置
├── railway.json          # Railway服务配置
├── requirements.txt      # 项目依赖
└── README.md            # 项目说明文档
```

## 许可证

本项目采用MIT许可证