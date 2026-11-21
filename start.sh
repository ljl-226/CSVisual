#!/usr/bin/env bash
# CSVisual 一键启动脚本（macOS / Linux）
#
# 项目自 2026-10-10 起只有 Python 后端（server-py / FastAPI），
# Node 版 server/ 已归档到 build/_trash/。本脚本只启动 Python 后端 + 前端。
set -e

cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "=========================================================="
echo "   CSVisual 计算机可视化智能学习平台 - 一键启动"
echo "   后端: server-py (FastAPI)  前端: Vite"
echo "=========================================================="
echo

# ---------- 1. 检查 Python ----------
if ! command -v python3 >/dev/null 2>&1; then
    echo "[错误] 未检测到 Python3，请先安装 Python 3.10+。"
    exit 1
fi
PYV=$(python3 -c 'import sys;print(".".join(map(str,sys.version_info[:3])))')
echo "[1/5] Python: $PYV"

# ---------- 2. 检查 Node.js（前端需要）----------
if ! command -v node >/dev/null 2>&1; then
    echo "[错误] 未检测到 Node.js，前端无法启动。"
    echo "       请先安装 Node.js 18+ : https://nodejs.org/zh-cn/download"
    exit 1
fi
echo "[2/5] Node.js: $(node -v)"

# ---------- 3. 检查 MySQL ----------
if command -v lsof >/dev/null 2>&1; then
    MYSQL_UP=$(lsof -i :3306 -sTCP:LISTEN >/dev/null 2>&1 && echo yes || echo no)
elif command -v ss >/dev/null 2>&1; then
    MYSQL_UP=$(ss -lnt 2>/dev/null | grep -q ':3306' && echo yes || echo no)
else
    MYSQL_UP="unknown"
fi
if [ "$MYSQL_UP" = "no" ]; then
    echo "[警告] 未检测到 MySQL（3306 端口未监听）。"
    printf "仍要继续吗？(y/n): "
    read -r GOON
    [ "$GOON" = "y" ] || exit 1
else
    echo "[3/5] MySQL 服务已启动"
fi

# ---------- 4. 准备 Python 后端 ----------
if [ ! -d "$ROOT/server-py/.venv" ]; then
    echo "[4/5] 创建 Python 虚拟环境..."
    python3 -m venv "$ROOT/server-py/.venv"
fi
if [ ! -f "$ROOT/server-py/.venv/.deps_ready" ]; then
    echo "       安装后端依赖（首次较慢）..."
    "$ROOT/server-py/.venv/bin/python" -m pip install -q --upgrade pip
    "$ROOT/server-py/.venv/bin/python" -m pip install -q -r "$ROOT/server-py/requirements.txt"
    touch "$ROOT/server-py/.venv/.deps_ready"
else
    echo "[4/5] 后端依赖已安装"
fi

if [ ! -f "$ROOT/server-py/.env" ]; then
    cp "$ROOT/server-py/.env.example" "$ROOT/server-py/.env"
    echo "       已生成 server-py/.env（请把 DB_PASSWORD 改成你的 MySQL 密码）"
fi

if [ ! -d "$ROOT/web/node_modules" ]; then
    echo "       安装前端依赖（首次较慢）..."
    (cd "$ROOT/web" && npm install --no-audit --no-fund)
fi

# ---------- 5. 初始化数据库 ----------
echo
echo "[5/5] 初始化数据库..."
if ! (cd "$ROOT/server-py" && PYTHONPATH="$ROOT/server-py" .venv/bin/python -m app.scripts.initdb); then
    echo
    echo "[错误] 数据库初始化失败。常见原因："
    echo "       1. MySQL 账号或密码不对 —— 打开 server-py/.env 修改 DB_PASSWORD"
    echo "       2. 该账号没有建库权限 —— 换用 root 账号"
    echo "       3. MySQL 没启动"
    exit 1
fi
echo "       数据库就绪"

# ---------- 6. 启动服务 ----------
echo
echo "正在启动服务..."
cd "$ROOT/server-py"
PYTHONPATH="$ROOT/server-py" nohup .venv/bin/python run.py > server-py.log 2>&1 &
echo $! > "$ROOT/.server.pid"
cd "$ROOT/web"
nohup npx vite --port 5173 > web.log 2>&1 &
echo $! > "$ROOT/.web.pid"
cd "$ROOT"

sleep 6

echo
echo "=========================================================="
echo "   启动完成！"
echo "   访问地址: http://localhost:5173        （前端热更新）"
echo "             http://localhost:3000        （后端直出 web/dist）"
echo "   接口文档: http://localhost:3000/docs"
echo
echo "   测试账号:"
echo "     学生   student / 123456"
echo "     管理员 admin   / admin123"
echo
echo "   日志: server-py/server-py.log  web/web.log"
echo "   停止: ./stop.sh"
echo "=========================================================="

if command -v open >/dev/null 2>&1; then
    open http://localhost:5173
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:5173
fi
