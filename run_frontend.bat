@echo off
title Virtual Lab - Frontend (React + Vite)
chcp 65001 > nul
cd /d %~dp0frontend
echo ===================================================
echo   در حال اجرای سرور فرانت‌اند Vite روی پورت 5173...
echo ===================================================
call npm.cmd run dev -- --host 0.0.0.0 --port 5173
pause
