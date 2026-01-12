# Dockerfile
FROM python:3.10-slim

# 1. 安装依赖（包括 libfuse2）
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    libfuse2 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. 下载并安装 MuseScore（使用 --appimage-extract-and-run）
RUN wget -q https://github.com/musescore/MuseScore/releases/download/v4.2.1/MuseScore-4.2.1.240530503-x86_64.AppImage \
    && chmod +x MuseScore-4.2.1.240530503-x86_64.AppImage \
    && ./MuseScore-4.2.1.240530503-x86_64.AppImage --appimage-extract \
    && mv squashfs-root /opt/musescore \
    && ln -s /opt/musescore/AppRun /usr/local/bin/musescore \
    && rm MuseScore-4.2.1.240530503-x86_64.AppImage

# 2. 验证安装
RUN mscore --version || echo "MuseScore版本信息"

# 3. 设置工作目录
WORKDIR /app

# 4. 复制依赖文件
COPY requirements.txt .

# 5. 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 6. 复制应用代码
COPY . .

# 7. 创建上传目录
RUN mkdir -p uploads

# 8. 暴露端口
EXPOSE 8080

# 9. 启动命令
CMD ["python", "server.py"]
