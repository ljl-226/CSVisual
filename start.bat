@echo off
chcp 65001 >nul
REM ============================================================
REM  CSVisual 一键启动
REM
REM  项目自 2026-10-10 起只有 Python 后端（server-py / FastAPI），
REM  Node 版 server/ 已归档到 build\_trash\。
REM
REM  本文件只做转发 —— 真正的逻辑在 start-python.bat，避免两处维护。
REM  双击本脚本与双击 start-python.bat 完全等价。
REM ============================================================
call "%~dp0start-python.bat" %*
