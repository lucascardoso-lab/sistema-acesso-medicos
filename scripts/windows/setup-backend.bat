@echo off
cd /d "%~dp0..\..\backend"
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
if not exist .env (
    copy .env.example .env
    echo Arquivo .env criado a partir de .env.example - edite com suas credenciais locais.
)
echo Setup do backend concluido. Rode "alembic upgrade head" apos configurar o .env.
