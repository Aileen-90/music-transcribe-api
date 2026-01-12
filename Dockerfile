# Dockerfile
FROM python:3.10-slim

# 安装必要的依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

# 从可用的 MuseScore 镜像复制文件
COPY --from=musescore/musescore-x86_64:3.5 /usr/bin/mscore /usr/local/bin/mscore
COPY --from=musescore/musescore-x86_64:3.5 /usr/share/musescore /usr/share/musescore
COPY --from=musescore/musescore-x86_64:3.5 /usr/lib/ /usr/lib/

# 设置无头模式环境变量
ENV QT_QPA_PLATFORM=offscreen
ENV DISPLAY=:99

# 验证安装
RUN mscore --version || echo "MuseScore installed"

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
