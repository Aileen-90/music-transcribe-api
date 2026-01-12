# Dockerfile
FROM python:3.10-slim

# 1. 安装依赖
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. 下载 appimagetool 并使用它提取
RUN wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage \
    && chmod +x appimagetool-x86_64.AppImage \
    && wget -q https://github.com/musescore/MuseScore/releases/download/v4.2.1/MuseScore-4.2.1.240530503-x86_64.AppImage \
    && mkdir -p /opt/musescore \
    && cd /opt/musescore \
    && /appimagetool-x86_64.AppImage --appimage-extract \
    && mv squashfs-root/AppRun ./ \
    && /appimagetool-x86_64.AppImage --appimage-extract MuseScore-4.2.1.240530503-x86_64.AppImage \
    && ln -s /opt/musescore/AppRun /usr/local/bin/musescore \
    && rm -f /appimagetool-x86_64.AppImage /MuseScore-4.2.1.240530503-x86_64.AppImage

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
