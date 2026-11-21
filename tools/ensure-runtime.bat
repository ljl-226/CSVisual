@echo off
rem ============================================================
rem  CSVisual built-in toolchain - readiness check (ASCII ONLY)
rem
rem  Called by start.bat / start-python.bat before the server
rem  starts. Safe to run on its own too.
rem
rem  Why: the built-in toolchain is optional - the server starts
rem  fine without it, and users would only discover that C/C++/Java
rem  cannot run when they first click "Run". Better to fix it up
rem  front: --ensure --auto deploys automatically, no prompt, so
rem  a fresh copy of the project becomes fully usable by itself.
rem
rem  NOTE: keep this file ASCII-only. cmd.exe parses batch files with
rem  the current code page; UTF-8 Chinese text plus "chcp" can shift
rem  line boundaries and get comments executed as commands.
rem  All Chinese output is printed by tools\setup_runtime.py --ensure.
rem
rem  Arg %1 = python.exe to use for deployment (optional).
rem  Always returns 0 - this is part of startup and must not block it.
rem ============================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

set "PYCMD="
if exist "%~1" set "PYCMD="%~1""

rem Validate candidates by actually running them - "where python" alone
rem is not enough (the "py" launcher may point at a removed interpreter,
rem and the Store alias "python" is a stub).
if not defined PYCMD ( python -c "import sys" >nul 2>nul && set "PYCMD=python" )
if not defined PYCMD ( py -3 -c "import sys" >nul 2>nul && set "PYCMD=py -3" )
if not defined PYCMD ( python3 -c "import sys" >nul 2>nul && set "PYCMD=python3" )

if not defined PYCMD goto no_python

call %PYCMD% "tools\setup_runtime.py" --ensure --auto
exit /b 0

:no_python
if exist "runtime\c-cpp\bin\gcc.exe" (
  echo [toolchain] built-in toolchain ready ^(runtime\^)
) else (
  echo [toolchain] not deployed, and no working Python found to deploy it.
  echo             Please run tools\setup-runtime.bat manually later.
)
exit /b 0
