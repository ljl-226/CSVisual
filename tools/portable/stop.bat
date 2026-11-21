@echo off
REM 与 start.bat 一样保持 GBK 编码、且不要中途 chcp，详见 start.bat 顶部说明
setlocal EnableDelayedExpansion
cd /d "%~dp0"

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "MYSQL=%ROOT%\runtime\mysql"
set "DBPORT=3307"
set "DBPWD=csvisual"
set "WEBPORT=3000"

echo 正在停止 CSVisual 服务...

REM ---------- 停后端：按端口找进程，比按进程名杀安全 ----------
REM netstat 输出第 5 列是 PID，同一个端口可能有多行（IPv4/IPv6），都杀掉。
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%WEBPORT% " ^| findstr "LISTENING"') do (
  taskkill /F /PID %%p >nul 2>nul
)

REM ---------- 停数据库：走正常的 shutdown，避免直接 kill 导致 InnoDB 需要崩溃恢复 ----------
if exist "%MYSQL%\bin\mysqladmin.exe" (
  "%MYSQL%\bin\mysqladmin.exe" -uroot -p%DBPWD% -h127.0.0.1 -P%DBPORT% shutdown >nul 2>nul
)
REM 上面没停掉（比如密码不对 / 不是本程序起的），再按端口兜底
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%DBPORT% " ^| findstr "LISTENING"') do (
  taskkill /F /PID %%p >nul 2>nul
)

ping -n 3 127.0.0.1 >nul
echo 已停止。
REM 卸载程序调用时会带 --silent，那种场合不能停在「请按任意键继续」上
if /i not "%1"=="--silent" (
  echo.
  pause
)
