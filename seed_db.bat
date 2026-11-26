@echo off
title Virtual Lab - Seed Database
chcp 65001 > nul
cd /d %~dp0
echo در حال مقداردهی اولیه پایگاه داده و کاربران پیش فرض...
python -m backend.app.seed
pause
