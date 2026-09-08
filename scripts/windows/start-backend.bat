@echo off
cd /d "%~dp0..\..\backend"
call venv\Scripts\activate.bat
uvicorn app.main:app --reload
