# 使用稳定的 Debian Bullseye 作为基础镜像
FROM python:3.11-bullseye

# 1. 安装系统依赖（确保 libgl1-mesa-glx 可用）
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
    libgbm1 \
    libfontconfig1 \
    libfreetype6 \
    libxrender1 \
    libxxf86vm1 \
    libxkbcommon-x11-0 \
    fonts-dejavu \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. 安装 MuseScore 3.5.2（优化安装方法）
RUN wget -q https://github.com/musescore/MuseScore/releases/download/v3.5.2/MuseScore-3.5.2.312125617-x86_64.AppImage \
    && chmod +x MuseScore-3.5.2.312125617-x86_64.AppImage \
    # 提取 AppImage 到 /opt/musescore
    && ./MuseScore-3.5.2.312125617-x86_64.AppImage --appimage-extract \
    && mv squashfs-root /opt/musescore \
    # 创建启动脚本，设置正确的环境变量
    && echo '#!/bin/bash\n\
# 设置 MuseScore 环境变量\n\
export LD_LIBRARY_PATH="/opt/musescore/usr/lib:$LD_LIBRARY_PATH"\n\
export QT_PLUGIN_PATH="/opt/musescore/usr/plugins"\n\
export QML2_IMPORT_PATH="/opt/musescore/usr/qml"\n\
# 执行 MuseScore\n\
exec /opt/musescore/AppRun "$@"' > /usr/local/bin/mscore \
    && chmod +x /usr/local/bin/mscore \
    && ln -sf /usr/local/bin/mscore /usr/local/bin/musescore \
    # 清理
    && rm -f MuseScore-3.5.2.312125617-x86_64.AppImage

# 3. 验证依赖并安装缺少的库
RUN ldd /opt/musescore/AppRun 2>/dev/null | grep "not found" | while read line; do \
        lib=$(echo $line | awk '{print $1}'); \
        echo "查找库: $lib"; \
        apt-get update && apt-get install -y apt-file && apt-file update; \
        pkg=$(apt-file search $lib | head -1 | cut -d: -f1) || true; \
        if [ ! -z "$pkg" ]; then \
            echo "安装 $pkg 以提供 $lib"; \
            apt-get install -y $pkg; \
        fi; \
    done || true

# 4. 验证 MuseScore 是否能运行
RUN Xvfb :99 -screen 0 1024x768x24 & \
    export DISPLAY=:99 && \
    export QT_QPA_PLATFORM=offscreen && \
    timeout 10 /usr/local/bin/mscore --version 2>&1 | head -5 && \
    echo "MuseScore 安装验证完成"

# 5. 设置工作目录
WORKDIR /app

# 6. 复制依赖文件（利用 Docker 缓存）
COPY requirements.txt .

# 7. 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 8. 复制应用代码
COPY server.py .

# 9. 创建必要的运行时目录
RUN mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix \
    && mkdir -p /tmp/runtime \
    && mkdir -p uploads \
    && chmod 755 uploads

# 10. 设置环境变量
ENV DISPLAY=:99
ENV QT_QPA_PLATFORM=offscreen
ENV QT_DEBUG_PLUGINS=0
ENV XDG_RUNTIME_DIR=/tmp/runtime
ENV LD_LIBRARY_PATH=/opt/musescore/usr/lib:$LD_LIBRARY_PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 11. 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# 12. 暴露端口（使用 Railway 的标准端口）
EXPOSE 8080

# 13. 启动命令（优化版本）
CMD ["sh", "-c", \
    "Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset & " \
    "sleep 3 && " \
    "export DISPLAY=:99 && " \
    "export QT_QPA_PLATFORM=offscreen && " \
    "python server.py"]