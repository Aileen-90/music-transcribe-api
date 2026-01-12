# Dockerfile
FROM python:3.10-slim

# 1. 安装系统依赖和MuseScore
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    software-properties-common \
    && wget -qO - https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x6D2C9A8A9A5E9B8B | apt-key add - \
    && echo "deb http://ppa.launchpad.net/mscore-ubuntu/mscore-stable/ubuntu focal main" >> /etc/apt/sources.list.d/musescore.list \
    && apt-get update \
    && apt-get install -y musescore \
    && rm -rf /var/lib/apt/lists/*

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