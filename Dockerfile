# Dockerfile
FROM python:3.10-slim

# 1. 安装依赖
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    tar \
    xz-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 2. 尝试下载并显示详细信息
RUN curl -v -L -o musescore.tar.xz https://github.com/musescore/MuseScore/releases/download/v4.2.1/MuseScore-4.2.1.240530503-linux-x86_64.tar.xz \
    && echo "下载完成，文件大小:" && ls -lh musescore.tar.xz \
    && tar -xf musescore.tar.xz -C /opt \
    && mv /opt/MuseScore-4.2.1.240530503-linux-x86_64 /opt/musescore \
    && ln -s /opt/musescore/bin/mscore /usr/local/bin/mscore \
    && rm musescore.tar.xz

# 3. 验证
RUN /opt/musescore/bin/mscore --version 2>/dev/null || echo "MuseScore 安装完成"

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
