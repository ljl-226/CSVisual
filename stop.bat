@echo off
chcp 65001 >nul
setlocal

echo 正在停止 CSVisual 服务...
set STOPPED=0

for %%P in (3000 5173 5174 5175) do (
    for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":%%P " ^| findstr "LISTENING"') do (
        taskkill /PID %%i /F >nul 2>nul
        if not errorlevel 1 (
            echo   已停止端口 %%P (PID %%i)
            set STOPPED=1
        )
    )
)

if "%STOPPED%"=="0" (
    echo   没有发现正在运行的服务。
) else (
    echo   服务已全部停止。
)

echo.
pause
