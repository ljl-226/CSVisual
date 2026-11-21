#!/usr/bin/env bash
# CSVisual 停止服务（macOS / Linux）
cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "正在停止 CSVisual 服务..."

stopped=0
for f in "$ROOT/server/.server.pid" "$ROOT/web/.web.pid"; do
    if [ -f "$f" ]; then
        pid=$(cat "$f")
        if kill "$pid" 2>/dev/null; then
            echo "   已停止进程 $pid"
            stopped=1
        fi
        rm -f "$f"
    fi
done

for P in 3000 5173 5174 5175; do
    if command -v lsof >/dev/null 2>&1; then
        pid=$(lsof -ti :$P 2>/dev/null)
        if [ -n "$pid" ]; then
            kill -9 $pid 2>/dev/null && echo "   已停止端口 $P" && stopped=1
        fi
    fi
done

[ "$stopped" = "0" ] && echo "   没有发现正在运行的服务。" || echo "   服务已全部停止。"
