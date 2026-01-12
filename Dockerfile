# Dockerfile
FROM python:3.10-slim

# 1. 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    apt-transport-https \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. 添加 MuseScore PPA（使用官方方法）
RUN wget -qO- https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xF446F2715C632854AE37CFC57A9FB82F99C5E97F | gpg --dearmor > /usr/share/keyrings/musescore1.gpg \
    && wget -qO- https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xA465CB739A21C396FB7FC1C68F66051A3A258030 | gpg --dearmor > /usr/share/keyrings/musescore2.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/musescore1.gpg,/usr/share/keyrings/musescore2.gpg] http://ppa.launchpad.net/mscore-ubuntu/mscore-stable/ubuntu focal main" > /etc/apt/sources.list.d/musescore.list \
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
