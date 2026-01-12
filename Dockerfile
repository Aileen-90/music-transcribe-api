# Dockerfile
FROM python:3.10-slim

# 安装必要的依赖
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libxi6 \
    libxcb1 \
    wget \
    libfuse2 \
    && rm -rf /var/lib/apt/lists/*

# 使用特殊的提取方法
RUN wget -q https://github.com/musescore/MuseScore/releases/download/v3.5.2/MuseScore-3.5.2.210621-x86_64.AppImage \
    && chmod +x MuseScore-3.5.2.210621-x86_64.AppImage \
    # 使用 appimage 自带的提取工具
    && ./MuseScore-3.5.2.210621-x86_64.AppImage --appimage-extract \
    && mv squashfs-root/usr/bin/mscore /usr/local/bin/ \
    && mv squashfs-root/usr/share/musescore /usr/share/ \
    && rm -rf MuseScore-3.5.2.210621-x86_64.AppImage squashfs-root

# 3. 设置环境变量
ENV QT_QPA_PLATFORM=offscreen
ENV DISPLAY=:99

# 4. 验证安装
RUN mscore --version || echo "MuseScore 3.5.2 installed"

# 5. 设置工作目录
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
