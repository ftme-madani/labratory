@echo off
title Virtual Lab - Runner
chcp 65001 > nul
echo ================================================================
echo         سامانه هوشمند ازمایشگاه مجازی علوم تجربی
echo ================================================================
echo.
echo [1/2] در حال راه اندازی سرور بک اند (FastAPI)...
start "Virtual Lab Backend (Port 8000)" cmd /k "cd /d %~dp0 && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 2 /nobreak > nul

echo [2/2] در حال راه اندازی سرور فرانت اند (React Vite)...
start "Virtual Lab Frontend (Port 5173)" cmd /k "cd /d %~dp0frontend && call npm.cmd run dev -- --host 0.0.0.0 --port 5173"

echo.
echo ================================================================
echo  هر دو سرویس با موفقیت در پنجره های مجزا اجرا شدند!
echo.
echo  * ادرس سیستم (رایانه):            http://localhost:5173
echo  * ادرس شبکه برای گوشی (وای فای):   http://192.168.1.6:5173
echo  * مستندات خودکار API (سواگر):       http://localhost:8000/docs
echo ================================================================
echo.
pause
