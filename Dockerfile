# Dockerfile
FROM python:3.10-slim

# 1. 安装必要依赖
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. 下载并安装 .deb 包
RUN wget -q https://github.com/musescore/MuseScore/releases/download/v4.2.1/MuseScore-4.2.1.240530503-x86_64.deb -O /tmp/musescore.deb \
    && apt-get update \
    && apt-get install -y /tmp/musescore.deb 2>/dev/null || apt-get install -f -y \
    && rm /tmp/musescore.deb \
    && rm -rf /var/lib/apt/lists/*

# 3. 查找正确的命令路径并验证
RUN find /usr -name "*score*" -type f -executable 2>/dev/null | grep -v ".so" | head -5 || echo "查找可执行文件" \
    && (mscore --version || musescore --version || /usr/bin/mscore --version || /usr/bin/musescore --version || echo "MuseScore安装完成但命令名称可能不同") \
    && echo "可用的命令: mscore, musescore, mscore4 等"

# 4. 创建通用别名（确保命令可用）
RUN ln -sf /usr/bin/mscore /usr/local/bin/mscore 2>/dev/null || true \
    && ln -sf /usr/bin/musescore /usr/local/bin/musescore 2>/dev/null || true \
    && ln -sf /usr/bin/mscore4 /usr/local/bin/mscore4 2>/dev/null || true

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
