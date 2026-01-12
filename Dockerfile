# Dockerfile - Railway 专用 MIDI转PDF服务
FROM python:3.11-bullseye

# 1. 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    fuse \
    xvfb \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libnss3 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libgbm-dev \
    libxkbcommon-x11-0 \
    libxrender1 \
    libxxf86vm1 \
    libfontconfig1 \
    libfreetype6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. 安装 MuseScore
RUN wget -q https://github.com/musescore/MuseScore/releases/download/v3.5.2/MuseScore-3.5.2.312125617-x86_64.AppImage \
    && chmod +x MuseScore-3.5.2.312125617-x86_64.AppImage \
    && ./MuseScore-3.5.2.312125617-x86_64.AppImage --appimage-extract \
    # 复制可执行文件
    && cp squashfs-root/AppRun /usr/local/bin/mscore \
    && chmod +x /usr/local/bin/mscore \
    # 复制库文件
    && cp -r squashfs-root/usr/lib/* /usr/lib/ 2>/dev/null || true \
    # 创建必要的符号链接
    && ln -sf /usr/local/bin/mscore /usr/local/bin/musescore \
    # 清理
    && rm -rf MuseScore-3.5.2.312125617-x86_64.AppImage squashfs-root

# 3. 验证安装
RUN ldd /usr/local/bin/mscore | grep -q "not found" && echo "警告：有未找到的依赖" || echo "依赖检查通过"

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
