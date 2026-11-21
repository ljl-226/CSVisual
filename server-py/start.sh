#!/usr/bin/env bash
# CSVisual 后端服务（Python / FastAPI）启动脚本
set -e

cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "=========================================================="
echo "   CSVisual 后端服务（Python / FastAPI）- 一键启动"
echo "=========================================================="
echo

# ---------- 1. 检查 Python ----------
PY=""
for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
    echo "[错误] 未检测到 Python，请先安装 Python 3.10 或更高版本。"
    exit 1
fi
echo "[1/4] Python 已安装: $($PY -c 'import sys;print(sys.version.split()[0])')"

# ---------- 2. 虚拟环境 + 依赖 ----------
if [ ! -x "$ROOT/.venv/bin/python" ]; then
    echo "[2/4] 首次运行，创建虚拟环境..."
    "$PY" -m venv "$ROOT/.venv"
else
    echo "[2/4] 虚拟环境已存在"
fi

if [ ! -f "$ROOT/.venv/.deps_ready" ]; then
    echo "      安装依赖（首次较慢，请耐心等待）..."
    "$ROOT/.venv/bin/python" -m pip install --upgrade pip -q
    "$ROOT/.venv/bin/python" -m pip install -r "$ROOT/requirements.txt" -q
    touch "$ROOT/.venv/.deps_ready"
else
    echo "      依赖已安装"
fi

# ---------- 3. 初始化数据库 ----------
echo
echo "[3/4] 初始化数据库（建库建表 + 导入课程与题库）..."
export PYTHONPATH="$ROOT"
if ! "$ROOT/.venv/bin/python" -m app.scripts.initdb; then
    echo
    echo "[错误] 数据库初始化失败。常见原因："
    echo "       1. MySQL 没启动，或 3306 端口未监听"
    echo "       2. MySQL 账号或密码不对 —— 编辑 server/.env 里的 DB_PASSWORD"
    echo "       3. 该账号没有建库权限 —— 换用 root 账号"
    exit 1
fi
echo "      数据库就绪"

# ---------- 4. 启动服务 ----------
echo
echo "[4/4] 启动后端服务..."
echo
echo "  接口地址: http://localhost:3000"
echo "  健康检查: http://localhost:3000/api/health"
echo "  接口文档: http://localhost:3000/docs"
echo
echo "  按 Ctrl+C 停止服务。"
echo "=========================================================="
echo

export PYTHONPATH="$ROOT"
exec "$ROOT/.venv/bin/python" run.py
