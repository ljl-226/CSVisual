@echo off
rem ============================================================
rem  CSVisual built-in toolchain - launcher (ASCII ONLY)
rem
rem  NOTE: keep this file ASCII-only. cmd.exe reads batch files
rem  byte-by-byte using the current code page; UTF-8 Chinese text
rem  mixed with "chcp" makes line boundaries drift and causes
rem  comment lines to be executed as commands.
rem  All Chinese output lives in tools\setup_runtime.py instead.
rem
rem  Double-click to deploy C/C++ and Java compilers into runtime\
rem  so that anyone who gets this project can run code without
rem  installing a compiler themselves.
rem ============================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

echo.
echo   ============================================================
echo    CSVisual - deploy built-in toolchain
echo   ============================================================
echo.

rem Pick a Python that actually runs. "where python" is not enough:
rem the "py" launcher can point at a Python that has since been moved
rem or uninstalled, and the Store alias "python" is a stub.
set "PYCMD="
python -c "import sys" >nul 2>nul && set "PYCMD=python"
if not defined PYCMD ( py -3 -c "import sys" >nul 2>nul && set "PYCMD=py -3" )
if not defined PYCMD ( python3 -c "import sys" >nul 2>nul && set "PYCMD=python3" )
if not defined PYCMD (
  echo   [x] No working Python found.
  echo       The backend itself is written in Python, so it should be installed.
  echo       Get it from https://www.python.org/downloads/ and tick
  echo       "Add python.exe to PATH" during setup.
  echo.
  pause
  exit /b 1
)

call %PYCMD% "tools\setup_runtime.py" %*

echo.
echo   ------------------------------------------------------------
echo    Restart the backend afterwards  (stop.bat, then start-python.bat)
echo    Check current status :  tools\setup-runtime.bat --info
echo    Remove built-in chain:  tools\setup-runtime.bat --clean
echo   ------------------------------------------------------------
echo.
pause
