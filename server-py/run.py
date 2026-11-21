"""服务启动入口（等价 Node 版的 npm start）。

    python run.py            # 启动到 .env 里的 PORT（默认 3000）
    python run.py --port 3001
    python run.py --initdb   # 先跑数据库初始化再启动
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    argv = sys.argv[1:]

    if '--initdb' in argv:
        argv.remove('--initdb')
        code = subprocess.call([sys.executable, '-m', 'app.scripts.initdb'], cwd=os.path.dirname(os.path.abspath(__file__)))
        if code != 0:
            sys.exit(code)

    if '--migrate' in argv:
        argv.remove('--migrate')
        code = subprocess.call([sys.executable, '-m', 'app.scripts.migrate'], cwd=os.path.dirname(os.path.abspath(__file__)))
        if code != 0:
            sys.exit(code)

    # --port 必须在 import app.core.config 之前写进环境变量。
    # 原先写在 import 之后，而 config 在导入时就把 PORT 读成了模块级常量，
    # 于是 os.environ 改了、config.PORT 还是旧值 —— 表现为
    # 「打印说启动在 3100，实际却去 bind 3000」，端口被占用时直接崩。
    if '--port' in argv:
        idx = argv.index('--port')
        os.environ['PORT'] = argv[idx + 1]
        del argv[idx:idx + 2]

    from app.core.config import PORT
    from app.main import main as run_server

    print(f'CSVisual 后端服务已启动: http://localhost:{os.getenv("PORT", PORT)}')
    print(f"数据库: {os.getenv('DB_HOST', '127.0.0.1')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'cs_visual')}")
    print('大模型: ' + (f"已配置({os.getenv('LLM_MODEL', '')})" if os.getenv('LLM_API_KEY') else '未配置 → 使用本地知识库降级回答'))
    run_server()


if __name__ == '__main__':
    main()
