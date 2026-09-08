@echo off
REM Sobe backend (uvicorn --reload) e frontend (vite) em janelas separadas.
start "Backend - uvicorn" cmd /k "%~dp0start-backend.bat"
start "Frontend - vite" cmd /k "%~dp0start-frontend.bat"
