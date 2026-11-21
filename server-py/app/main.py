"""CSVisual 后端服务入口（FastAPI 版）。

路由前缀与 Node/Express 版完全一致（/api/auth、/api/course ...），
前端无需任何改动即可切换到本服务。
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.body import JsonBodyMiddleware
from app.core.config import IS_PROD, JWT_SECRET, PORT
from app.core.errors import register_exception_handlers
from app.core.shield import SecurityMiddleware
from app.db import ping
from app.routers import (admin, agent, algorithm, auth, code, course, feedback,
                         learn, question)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1) 增量迁移：建表、补列、导入种子（幂等）
    try:
        from app.scripts.migrate import run as run_migrate

        done = run_migrate()
        if done:
            print('数据库结构已更新: ' + '; '.join(done))
    except Exception as e:
        print('数据库迁移失败:', e)

    # 2) 数据体检：清掉指向不存在父记录的孤儿行（会让详情页 404、前端出现空白卡片）。
    #    修复前自动备份到 server-py/backups/，出问题可回滚。
    try:
        from app.scripts.repair import repair

        result = repair(dry_run=False, quiet=True)
        if result.get('changed'):
            print(f"数据体检：清理了 {result['changed']} 行脏数据，备份见 {result.get('backup')}")
    except Exception as e:
        print('数据体检失败:', e)
    yield


PLACEHOLDER_SECRET = 'csvisual_secret_key_change_me'


def create_app() -> FastAPI:
    # 生产环境带着源码里的公开密钥上线，等于把管理员令牌的签发权交给任何人
    if IS_PROD and (not JWT_SECRET or JWT_SECRET == PLACEHOLDER_SECRET):
        raise SystemExit(
            '[FATAL] 生产环境必须设置 JWT_SECRET，且不能使用占位值 ' + PLACEHOLDER_SECRET +
            '。可用 python -c "import secrets;print(secrets.token_hex(48))" 生成。'
        )
    app = FastAPI(title='CSVisual Server', version='1.0.0', lifespan=lifespan)

    # 中间件顺序：Starlette 是「后添加的在外层」，所以 Security 最后加，
    # 让它最先看到请求 —— 来源不合法 / 超配额的请求在最外层就被打回，
    # 不必再读一遍 body。CORS 也由它统一处理（按 ALLOWED_ORIGINS 白名单，
    # 不再无条件 allow_origins=['*']）。
    app.add_middleware(JsonBodyMiddleware)
    app.add_middleware(SecurityMiddleware)

    register_exception_handlers(app)

    # 静态资源目录：必须先建出来再挂载 —— StaticFiles 不接受不存在的目录，
    # 而头像上传接口在第一次有人换头像时才写文件，晚于这里的启动流程
    # server-py/ （main.py → app → server-py）
    _BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    uploads = os.path.join(_BASE, 'uploads')
    os.makedirs(os.path.join(uploads, 'avatars'), exist_ok=True)
    app.mount('/uploads', StaticFiles(directory=uploads), name='uploads')

    @app.get('/api/health')
    def health():
        db_ok = ping()
        return {
            'code': 200,
            'data': {
                'service': 'CSVisual Server',
                'db': 'connected' if db_ok else 'disconnected',
                'llm': 'configured' if os.getenv('LLM_API_KEY') else 'fallback(local-kb)',
                'runtime': 'python-fastapi',
                'time': datetime.now().isoformat(),
            },
        }

    @app.get('/api/stats')
    def public_stats():
        """登录页 / 首页展示用的公开统计。全部来自数据库实时计数，
        避免像以前那样把「9 门课程」写死在页面里，加了课程就再也对不上。"""
        from app.db import query_one
        from app.routers.code import LANGS

        def one(sql, default=0):
            try:
                row = query_one(sql)
                return int((row or {}).get('c') or default)
            except Exception:
                return default

        return {
            'code': 200,
            'data': {
                'courses': one('SELECT COUNT(*) AS c FROM course'),
                'knowledge': one('SELECT COUNT(*) AS c FROM knowledge'),
                'visualizations': one("SELECT COUNT(*) AS c FROM knowledge WHERE route LIKE '/vis/%'"),
                'codeLabs': one("SELECT COUNT(*) AS c FROM knowledge WHERE route LIKE '/code/%'"),
                # 在线运行支持的编程语言数（C / C++ / Java / Python / JavaScript）
                'languages': len(LANGS),
                'questions': one('SELECT COUNT(*) AS c FROM question'),
                'algorithms': one('SELECT COUNT(*) AS c FROM algorithm'),
            },
        }

    app.include_router(auth.router, prefix='/api/auth')
    app.include_router(course.router, prefix='/api/course')
    app.include_router(question.router, prefix='/api/question')
    app.include_router(learn.router, prefix='/api/learn')
    app.include_router(agent.router, prefix='/api/agent')
    app.include_router(admin.router, prefix='/api/admin')
    app.include_router(feedback.router, prefix='/api/feedback')
    app.include_router(code.router, prefix='/api/code')
    app.include_router(algorithm.router, prefix='/api/algorithm')

    # 前端构建产物托管：Node 后端原本的能力，收敛到 Python 后端后必须保留，
    # 否则打包/离线部署时整个系统只剩接口、没有页面。
    # 目录不存在（开发态跑 vite dev :5173）就跳过，不影响接口服务。
    #
    # 必须放在所有 /api 路由**之后**注册：这是个 /{full_path:path} 通吃路由，
    # 注册早了会把 /api/health 之类也吞掉（实测表现为「接口返回 index.html」）。
    web_dist = os.getenv('WEB_DIST') or os.path.join(os.path.dirname(_BASE), 'web', 'dist')
    if os.path.isdir(web_dist):
        assets = os.path.join(web_dist, 'assets')
        if os.path.isdir(assets):
            app.mount('/assets', StaticFiles(directory=assets), name='web-assets')

        from fastapi.responses import FileResponse

        _root = os.path.realpath(web_dist)

        @app.get('/{full_path:path}')
        def spa(full_path: str):
            """SPA 兜底：dist 里命中的静态文件直出，否则回 index.html 交给前端路由。"""
            target = os.path.realpath(os.path.join(_root, full_path or ''))
            # 目录穿越防护：只允许落在 dist 目录内
            if target.startswith(_root + os.sep) and os.path.isfile(target):
                return FileResponse(target)
            return FileResponse(os.path.join(_root, 'index.html'))

    return app


app = create_app()


def main():
    import uvicorn

    print(f'CSVisual 后端服务已启动: http://localhost:{PORT}')
    print(f"数据库: {os.getenv('DB_HOST', '127.0.0.1')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'cs_visual')}")
    print('大模型: ' + (f"已配置({os.getenv('LLM_MODEL', '')})" if os.getenv('LLM_API_KEY') else '未配置 → 使用本地知识库降级回答'))
    uvicorn.run(app, host='0.0.0.0', port=PORT, log_level='info')


if __name__ == '__main__':
    main()
