@echo off
title Laya Snake Game
cd /d "%~dp0"
echo ======================================================
echo           Starting Laya System 1 Game Server
echo           Model: C:\AI\Models\laya
echo ======================================================
echo.
echo Opening game in your default browser...
start "" "http://localhost:8080/snake"
echo.
echo Running server... (Press Ctrl+C to stop)
python -u server.py
pause
