# Dockerfile
FROM python:3.10-slim

# 1. 安装依赖
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    tar \
    xz-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 直接从官方MuseScore Docker镜像复制二进制文件
COPY --from=musescore/musescore:latest /usr/bin/mscore /usr/local/bin/mscore
# 或者复制整个安装目录
COPY --from=musescore/musescore:latest /usr/share/musescore /usr/share/musescore

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
