@echo off
title Code Optimization Framework - Embedded Systems

echo ========================================
echo  Code Optimization Framework
echo  Embedded Systems Compiler Capstone
echo ========================================
echo.

echo [1/2] Starting Backend (FastAPI on port 8000)...
start "Backend - FastAPI" cmd /k "cd /d "%~dp0backend" && python -m uvicorn api.main:app --host 127.0.0.1 --port 8000"

echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend (Vite on port 5173)...
start "Frontend - Vite" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo Waiting for frontend to initialize...
timeout /t 4 /nobreak >nul

echo.
echo ========================================
echo  Both servers are starting up!
echo.
echo  Frontend : http://localhost:5173
echo  Backend  : http://127.0.0.1:8000
echo  API Docs : http://127.0.0.1:8000/docs
echo ========================================
echo.
echo Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:5173

echo.
echo Press any key to close this window.
echo (The backend and frontend windows will keep running)
pause >nul
