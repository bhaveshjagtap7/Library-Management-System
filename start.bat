@echo off
title Enterprise Smart Library Management Platform
cd /d "%~dp0"
echo ========================================================
echo Starting Enterprise Smart Library Management Platform...
echo ========================================================
echo.
echo URL: http://localhost:5000
echo.
.venv\Scripts\python.exe run.py
pause
