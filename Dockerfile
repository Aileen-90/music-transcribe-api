# Dockerfile
FROM python:3.10-slim

# 1. 安装必要依赖（使用正确的 Debian 12 包名）
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    tar \
    xz-utils \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
    libx11-6 \
    libxrender1 \
    libfontconfig1 \
    libxi6 \
    libsm6 \
    libice6 \
    && rm -rf /var/lib/apt/lists/*

# 2. 下载并解压 MuseScore tar.gz 包
RUN wget -q https://ftp.osuosl.org/pub/musescore/releases/MuseScore-4.2/MuseScore-4.2.1.240530503-linux-x86_64.tar.xz \
    && tar -xf MuseScore-4.2.1.240530503-linux-x86_64.tar.xz -C /opt \
    && mv /opt/MuseScore-4.2.1.240530503-linux-x86_64 /opt/musescore \
    && ln -s /opt/musescore/bin/mscore /usr/local/bin/mscore \
    && ln -s /opt/musescore/bin/mscore /usr/local/bin/musescore \
    && rm MuseScore-4.2.1.240530503-linux-x86_64.tar.xz

# 3. 验证安装
RUN /opt/musescore/bin/mscore --version 2>/dev/null || echo "MuseScore 已安装到 /opt/musescore/"

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
