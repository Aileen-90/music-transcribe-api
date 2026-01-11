# backend/railway_config.py
import os

# Railway 会自动设置 PORT 环境变量
port = int(os.environ.get("PORT", 5000))

# 修改 server.py 的最后部分
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)  # 生产环境关掉debug