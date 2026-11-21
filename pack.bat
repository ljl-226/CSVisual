@echo off
rem ============================================================
rem  CSVisual share bundle - launcher (ASCII ONLY, keep it that way)
rem
rem  NOTE: this file must stay ASCII-only and CRLF-terminated.
rem  cmd.exe parses batch files byte-by-byte against the current code
rem  page; UTF-8 Chinese lines occasionally get split at the wrong byte
rem  and then run as commands. It reproduced while packing the full
rem  bundle (the branch that includes runtime\):
rem
rem      '...' is not recognized as an internal or external command
rem      operable program or batch file.
rem
rem  The script still finished, but users saw a meaningless error line
rem  and could not tell whether packaging succeeded. So all the real
rem  work and every Chinese message now live in tools\pack.py.
rem
rem  Double-click to produce the share zip. Flags pass straight through:
rem      pack.bat --no-runtime     bundle without the built-in toolchain
rem      pack.bat --out D:\a.zip   choose the output path
rem ============================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo.
echo   ============================================================
echo    CSVisual - pack a share bundle
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
  echo       This project needs Python either way - the recommended
  echo       backend is FastAPI. Get it from
  echo       https://www.python.org/downloads/
  echo       and tick "Add python.exe to PATH" during setup.
  echo.
  pause
  exit /b 1
)

call %PYCMD% "tools\pack.py" %*

echo.
pause
