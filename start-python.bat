@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

cd /d "%~dp0"
set "ROOT=%~dp0"

REM 被 start.bat 调用时传 --no-pause：那种情况下不该再 pause，
REM 否则父脚本会卡在子脚本的「请按任意键继续」上。单独双击时仍然 pause。
set "NOPAUSE=0"
if /i "%~1"=="--no-pause" set "NOPAUSE=1"

echo ==========================================================
echo    CSVisual 一键启动（Python 后端 + 前端）
echo ==========================================================
echo.
echo   本脚本使用 server-py（FastAPI）作为后端。
echo   项目自 2026-10-10 起已收敛为纯 Python 后端，start.bat 与本脚本等价。
echo.

REM ---------- 1. 检查 Python ----------
where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 未检测到 Python。
    echo        请先安装 Python 3.10 或更高版本: https://www.python.org/downloads/
    echo        安装时务必勾选 "Add Python to PATH"，装完重新双击本脚本。
    echo.
    call :pause_if_needed
    exit /b 1
)
for /f "tokens=*" %%v in ('python -c "import sys;print(sys.version.split()[0])"') do set "PYV=%%v"
echo [1/5] Python 已安装: %PYV%

REM ---------- 2. 检查 Node.js（前端需要）----------
where node >nul 2>nul
if errorlevel 1 (
    echo [错误] 未检测到 Node.js，前端无法启动。
    echo        请安装 Node.js 18 或更高版本: https://nodejs.org/zh-cn/download
    echo.
    call :pause_if_needed
    exit /b 1
)
echo [2/5] Node.js 已安装

REM ---------- 3. 检查 MySQL ----------
netstat -ano | findstr ":3306" | findstr "LISTENING" >nul 2>nul
if errorlevel 1 (
    echo [警告] 未检测到 MySQL（3306 端口未监听）。
    echo        请先安装并启动 MySQL 5.7/8.0，否则数据库无法初始化。
    echo.
    set /p GOON=仍要继续吗？(y/n):
    if /i not "!GOON!"=="y" exit /b 1
) else (
    echo [3/5] MySQL 服务已启动
)

REM ---------- 4. 准备 Python 后端 ----------
if not exist "%ROOT%server-py\.venv\Scripts\python.exe" (
    echo [4/5] 首次运行，创建 Python 虚拟环境...
    python -m venv "%ROOT%server-py\.venv"
    if errorlevel 1 ( echo [错误] 虚拟环境创建失败。 & call :pause_if_needed & exit /b 1 )
) else (
    echo [4/5] Python 虚拟环境已存在
)

if not exist "%ROOT%server-py\.venv\.deps_ready" (
    echo       安装后端依赖（首次较慢，请耐心等待）...
    "%ROOT%server-py\.venv\Scripts\python.exe" -m pip install --upgrade pip -q
    "%ROOT%server-py\.venv\Scripts\python.exe" -m pip install -r "%ROOT%server-py\requirements.txt" -q
    if errorlevel 1 (
        echo [错误] 依赖安装失败。国内网络可试试手动执行：
        echo        server-py\.venv\Scripts\python.exe -m pip install -r server-py\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
        call :pause_if_needed & exit /b 1
    )
    echo done > "%ROOT%server-py\.venv\.deps_ready"
) else (
    echo       后端依赖已安装
)

if not exist "%ROOT%web\node_modules" (
    echo       安装前端依赖（首次较慢，请耐心等待）...
    pushd "%ROOT%web"
    call npm install --no-audit --no-fund
    if errorlevel 1 ( echo [错误] 前端依赖安装失败。 & popd & call :pause_if_needed & exit /b 1 )
    popd
) else (
    echo       前端依赖已安装
)

REM ---------- 5. 初始化数据库 ----------
echo.
echo [5/5] 初始化数据库（建库建表 + 导入课程与题库）...
pushd "%ROOT%server-py"
set "PYTHONPATH=%ROOT%server-py"
"%ROOT%server-py\.venv\Scripts\python.exe" -m app.scripts.initdb
if errorlevel 1 (
    echo.
    echo [错误] 数据库初始化失败。常见原因：
    echo        1. MySQL 账号或密码不对 —— 打开 server-py\.env 修改 DB_PASSWORD
    echo        2. 该账号没有建库权限 —— 换用 root 账号
    echo        3. MySQL 没启动
    echo.
    popd & call :pause_if_needed & exit /b 1
)
popd
echo       数据库就绪

REM ---------- 6. 内置编译器（决定「换台电脑还能不能运行代码」）----------
call "%ROOT%tools\ensure-runtime.bat" "%ROOT%server-py\.venv\Scripts\python.exe"

REM ---------- 7. 启动 ----------
echo.
echo 正在启动服务，会弹出两个新窗口（后端 / 前端），请勿关闭。
echo.
start "CSVisual 后端 :3000 (Python)" cmd /k "cd /d "%ROOT%server-py" && set PYTHONPATH=%ROOT%server-py && .venv\Scripts\python.exe run.py"
timeout /t 3 >nul
start "CSVisual 前端 :5173" cmd /k "cd /d "%ROOT%web" && npx vite --port 5173"

timeout /t 6 >nul
start "" http://localhost:5173

echo.
echo ==========================================================
echo   启动完成！
echo   访问地址: http://localhost:5173        （开发态，前端热更新）
echo              http://localhost:3000        （后端直出 web/dist，构建后可用）
echo   接口文档: http://localhost:3000/docs
echo.
echo   测试账号:
echo     学生   student / 123456
echo     管理员 admin   / admin123
echo.
echo   不用时请运行 stop.bat 停止服务
echo ==========================================================
echo.
call :pause_if_needed

REM ---------- 子过程：按需暂停 ----------
:pause_if_needed
if "%NOPAUSE%"=="0" pause
exit /b 0
