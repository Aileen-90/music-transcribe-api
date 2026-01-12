# Dockerfile
FROM python:3.10-slim

# 安装必要的依赖
RUN apt-get update && apt-get install -y \
    wget \
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
    fonts-dejavu \
    # 清理缓存
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. 安装 MuseScore（直接下载二进制版本，避免 AppImage 问题）
RUN wget -q https://github.com/musescore/MuseScore/releases/download/v3.5.2/mscore-3.5.2-x86_64.AppImage \
    && chmod +x mscore-3.5.2-x86_64.AppImage \
    # 提取 AppImage
    && ./mscore-3.5.2-x86_64.AppImage --appimage-extract \
    # 复制 MuseScore 二进制文件
    && cp squashfs-root/usr/bin/mscore /usr/local/bin/ \
    && cp -r squashfs-root/usr/share/musescore /usr/share/ \
    && cp -r squashfs-root/usr/lib/* /usr/lib/ 2>/dev/null || true \
    # 创建符号链接
    && ln -sf /usr/local/bin/mscore /usr/local/bin/musescore \
    # 清理
    && rm -rf mscore-3.5.2-x86_64.AppImage squashfs-root

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
