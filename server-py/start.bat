@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

cd /d "%~dp0"
set "ROOT=%~dp0"

echo ==========================================================
echo    CSVisual 后端服务（Python / FastAPI）- 一键启动
echo ==========================================================
echo.

REM ---------- 1. 检查 Python ----------
where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 未检测到 Python。
    echo        请先安装 Python 3.10 或更高版本: https://www.python.org/downloads/
    echo        安装时务必勾选 "Add Python to PATH"，装完重新双击本脚本。
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python -c "import sys;print(sys.version.split()[0])"') do set "PYV=%%v"
echo [1/4] Python 已安装: %PYV%

REM ---------- 2. 创建虚拟环境并安装依赖 ----------
if not exist "%ROOT%.venv\Scripts\python.exe" (
    echo [2/4] 首次运行，创建虚拟环境...
    python -m venv "%ROOT%.venv"
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败。
        pause & exit /b 1
    )
) else (
    echo [2/4] 虚拟环境已存在
)

if not exist "%ROOT%.venv\.deps_ready" (
    echo       安装依赖（首次较慢，请耐心等待）...
    "%ROOT%.venv\Scripts\python.exe" -m pip install --upgrade pip -q
    "%ROOT%.venv\Scripts\python.exe" -m pip install -r "%ROOT%requirements.txt" -q
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请检查网络后重试。
        echo        国内网络可试试: .venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
        pause & exit /b 1
    )
    echo done > "%ROOT%.venv\.deps_ready"
) else (
    echo       依赖已安装
)

REM ---------- 3. 初始化数据库 ----------
echo.
echo [3/4] 初始化数据库（建库建表 + 导入课程与题库）...
set "PYTHONPATH=%ROOT%"
"%ROOT%.venv\Scripts\python.exe" -m app.scripts.initdb
if errorlevel 1 (
    echo.
    echo [错误] 数据库初始化失败。常见原因：
    echo        1. MySQL 没启动，或 3306 端口未监听
    echo        2. MySQL 账号或密码不对 —— 编辑 server\.env 里的 DB_PASSWORD
    echo        3. 该账号没有建库权限 —— 换用 root 账号
    echo        4. MySQL 服务名不是默认的，请确认能连上 127.0.0.1:3306
    echo.
    pause & exit /b 1
)
echo       数据库就绪

REM ---------- 4. 内置编译器（决定「换台电脑还能不能运行代码」）----------
echo.
echo [4/5] 检查内置编译器...
call "%~dp0..\tools\ensure-runtime.bat" "%ROOT%.venv\Scripts\python.exe"

REM ---------- 5. 启动服务 ----------
echo.
echo [5/5] 启动后端服务...
echo.
echo   接口地址: http://localhost:3000
echo   健康检查: http://localhost:3000/api/health
echo   接口文档: http://localhost:3000/docs
echo.
echo   关闭本窗口即可停止服务。
echo ==========================================================
echo.

set "PYTHONPATH=%ROOT%"
"%ROOT%.venv\Scripts\python.exe" run.py

pause
