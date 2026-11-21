@echo off
REM ============================================================
REM 本文件以 GBK(936) 编码保存 —— 千万别改成 UTF-8！
REM
REM cmd.exe 读批处理是按系统 ANSI 代码页逐字节解析的，UTF-8 的中文
REM 在这里会让行边界漂移（表现为某几行被当成命令执行，冒出
REM "'xxx' 不是内部或外部命令"）。项目的 pack.bat 早期就踩过。
REM 好处是：本文件既然是 GBK，下面写 my.ini 时就不用再切代码页了 ——
REM mysqld 读选项文件同样按 ANSI 解析，两边天然一致。
REM
REM 另外：批处理里**千万不要中途 chcp**。cmd 会在切换后按新代码页重新解析
REM 剩下的内容，而文件指针还停在旧代码页算出的位置，于是后面的行被腰斩，
REM 冒出一堆「'xxx' 不是内部或外部命令」。开头切也一样会踩。
REM ============================================================
setlocal EnableDelayedExpansion
cd /d "%~dp0"

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "PY=%ROOT%\runtime\python\python.exe"
set "MYSQL=%ROOT%\runtime\mysql"
set "MYINI=%MYSQL%\my.ini"
set "DATA=%ROOT%\data\mysql"
set "DBPORT=3307"
set "DBPWD=csvisual"
set "WEBPORT=3000"

echo ==========================================================
echo   CSVisual 计算机可视化智能学习平台
echo ==========================================================
echo.

REM ---------- 1. 运行时就位检查 ----------
if not exist "%PY%" (
  echo [错误] 找不到 runtime\python\python.exe，安装不完整，请重新安装。
  echo.
  pause
  exit /b 1
)
if not exist "%MYSQL%\bin\mysqld.exe" (
  echo [错误] 找不到 runtime\mysql\bin\mysqld.exe，安装不完整，请重新安装。
  echo.
  pause
  exit /b 1
)
echo [1/5] 内置运行时检查通过

REM ---------- 2. 写数据库配置 ----------
REM 路径统一用正斜杠 —— MySQL 官方在 Windows 上推荐这么写，反斜杠会被当转义。
REM 本文件是 GBK 编码，echo 出来的内容天然就是 GBK，mysqld 能正确解析中文路径。
if not exist "%MYINI%" (
  echo [2/5] 首次运行，正在生成数据库配置...
  if not exist "%DATA%" mkdir "%DATA%"
  set "PF=%ROOT:\=/%"
  set "DF=%DATA:\=/%"
  > "%MYINI%" echo [mysqld]
  >> "%MYINI%" echo basedir=!PF!/runtime/mysql
  >> "%MYINI%" echo datadir=!DF!
  >> "%MYINI%" echo port=%DBPORT%
  >> "%MYINI%" echo bind-address=127.0.0.1
  >> "%MYINI%" echo default_authentication_plugin=mysql_native_password
  >> "%MYINI%" echo character-set-server=utf8mb4
  >> "%MYINI%" echo collation-server=utf8mb4_unicode_ci
  >> "%MYINI%" echo default-time-zone=+08:00
  >> "%MYINI%" echo skip-log-bin
  >> "%MYINI%" echo performance_schema=OFF
  >> "%MYINI%" echo innodb_buffer_pool_size=128M
  >> "%MYINI%" echo innodb_redo_log_capacity=32M
  >> "%MYINI%" echo max_connections=100
  >> "%MYINI%" echo symbolic-links=0
  >> "%MYINI%" echo.
  >> "%MYINI%" echo [client]
  >> "%MYINI%" echo port=%DBPORT%
  >> "%MYINI%" echo default-character-set=utf8mb4
) else (
  echo [2/5] 数据库配置已存在，跳过
)

REM ---------- 3. 首次初始化数据目录 ----------
set "FRESH=0"
dir /b /a "%DATA%" 2>nul | findstr /r "." >nul
if errorlevel 1 set "FRESH=1"

if "%FRESH%"=="1" (
  echo [3/5] 首次运行，正在初始化数据库（约 20-40 秒，请稍候）...
  "%MYSQL%\bin\mysqld.exe" --defaults-file="%MYINI%" --initialize-insecure --console > "%ROOT%\data\init.log" 2>&1
  if errorlevel 1 (
    echo.
    echo [错误] 数据库初始化失败，详细信息见 data\init.log：
    type "%ROOT%\data\init.log"
    echo.
    pause
    exit /b 1
  )
)

REM ---------- 4. 启动数据库 ----------
echo [4/5] 正在启动内置数据库（端口 %DBPORT%）...
start "CSVisual 数据库" /MIN "%MYSQL%\bin\mysqld.exe" --defaults-file="%MYINI%"

set "READY=0"
for /L %%i in (1,1,90) do (
  "%MYSQL%\bin\mysqladmin.exe" -uroot -h127.0.0.1 -P%DBPORT% ping >nul 2>nul
  if not errorlevel 1 (
    set "READY=1"
    goto :dbready
  )
  ping -n 2 127.0.0.1 >nul
)
:dbready
if "%READY%"=="0" (
  echo.
  echo [错误] 数据库启动超时（90 秒）。
  echo        常见原因：本机已有一个 MySQL 占用了 %DBPORT%，或杀毒软件拦截了 mysqld。
  echo        日志见 data\init.log 与 data\mysql\*.err
  echo.
  pause
  exit /b 1
)

REM ---------- 5. 首次导入数据 + 写应用配置 ----------
if not exist "%ROOT%\data\.imported" (
  echo [5/5] 首次运行，正在导入课程与题库（约 1-2 分钟，请稍候）...
  "%MYSQL%\bin\mysql.exe" -uroot -h127.0.0.1 -P%DBPORT% -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '%DBPWD%'; CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY '%DBPWD%'; GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION; FLUSH PRIVILEGES;"
  "%MYSQL%\bin\mysql.exe" -uroot -p%DBPWD% -h127.0.0.1 -P%DBPORT% < "%ROOT%\initdb\cs_visual.sql"
  if errorlevel 1 (
    echo [错误] 数据导入失败。
    pause
    exit /b 1
  )
  echo ok> "%ROOT%\data\.imported"
)

if not exist "%ROOT%\app\server-py\.env" (
  > "%ROOT%\app\server-py\.env" echo PORT=%WEBPORT%
  >> "%ROOT%\app\server-py\.env" echo DB_HOST=127.0.0.1
  >> "%ROOT%\app\server-py\.env" echo DB_PORT=%DBPORT%
  >> "%ROOT%\app\server-py\.env" echo DB_USER=root
  >> "%ROOT%\app\server-py\.env" echo DB_PASSWORD=%DBPWD%
  >> "%ROOT%\app\server-py\.env" echo DB_NAME=cs_visual
  >> "%ROOT%\app\server-py\.env" echo JWT_SECRET=csvisual_local_demo_secret
  >> "%ROOT%\app\server-py\.env" echo JWT_EXPIRES=7d
  REM 这里故意不写 WEB_DIST：本文件是 GBK，写进去的路径若含中文，
  REM Python 端按 UTF-8 读出来就是乱码，前端页面会全部 404。
  REM 后端现在会按自身位置找同级的 app\web，不需要我们把路径传进去。
  >> "%ROOT%\app\server-py\.env" echo LLM_API_KEY=
  >> "%ROOT%\app\server-py\.env" echo LLM_BASE_URL=https://api.deepseek.com/v1
  >> "%ROOT%\app\server-py\.env" echo LLM_MODEL=deepseek-flash
  >> "%ROOT%\app\server-py\.env" echo LLM_THINKING=0
)
if not exist "%ROOT%\app\server-py\uploads" mkdir "%ROOT%\app\server-py\uploads"

REM ---------- 6. 启动服务 ----------
echo.
echo 正在启动 CSVisual 服务...
REM Python 后端靠 run.py 所在的目录定位 app（脚本目录自动进 sys.path），
REM 所以必须 /D 到 app\server-py 再启；WEB_DIST 不写进 .env，
REM 后端会按自身位置找同级的 app\web。
start "CSVisual 服务" /D "%ROOT%\app\server-py" /MIN "%PY%" run.py

set "WEBREADY=0"
for /L %%i in (1,1,60) do (
  curl.exe -s -f -o nul "http://127.0.0.1:%WEBPORT%/api/health" >nul 2>nul
  if not errorlevel 1 (
    set "WEBREADY=1"
    goto :webready
  )
  ping -n 2 127.0.0.1 >nul
)
:webready

if "%WEBREADY%"=="1" (
  start "" "http://127.0.0.1:%WEBPORT%/"
) else (
  echo [警告] 服务 60 秒未响应，请稍等几秒后手动访问下面的地址。
)

echo.
echo ==========================================================
echo   启动完成！
echo.
echo   访问地址：http://127.0.0.1:%WEBPORT%
echo.
echo   测试账号：
echo     学生   student / 123456
echo     管理员 admin   / admin123
echo.
echo   用完后请运行「停止 CSVisual」关闭服务，
echo   否则数据库进程会一直留在后台。
echo ==========================================================
echo.
pause
