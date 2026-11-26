@echo off
title Virtual Lab - Backend (FastAPI)
chcp 65001 > nul
cd /d %~dp0
echo ===================================================
echo   در حال اجرای سرور بک‌اند FastAPI روی پورت 8000...
echo ===================================================
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
pause
