# Sistema de Cadastro, Validação e Liberação de Acesso de Médicos

Sistema web para cadastro, validação e liberação de acesso de médicos:
formulário público de solicitação + área administrativa para análise,
aprovação/rejeição e envio da resposta.

A especificação funcional e técnica completa está em
[`docs/BLUEPRINT.md`](docs/BLUEPRINT.md), incluindo o histórico de decisões
técnicas (seção 35).

## Stack

- **Frontend:** React + Vite + TypeScript
- **Backend:** Python + FastAPI + SQLAlchemy + Pydantic + Alembic
- **Banco de dados:** MySQL
- **Sem Docker**, em nenhuma etapa (dev ou produção)

## Desenvolvimento no Windows

Pré-requisitos: Python 3.11+, Node.js 18+, MySQL local em execução, e um
banco de dados já criado (ex.: `sistema_medicos`).

### 1. Backend

```bat
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edite `backend\.env` com suas credenciais locais (no mínimo `DATABASE_URL` e
`SECRET_KEY`). Depois rode as migrations e crie o usuário administrador
inicial:

```bat
alembic upgrade head
python -m scripts.seed_admin --nome "Seu Nome" --email admin@exemplo.com --senha "SenhaForte123!"
```

Suba o backend:

```bat
uvicorn app.main:app --reload
```

A API fica em `http://localhost:8000/api`, com documentação automática em
`http://localhost:8000/docs`.

### 2. Frontend

```bat
cd frontend
npm install
npm run dev
```

O frontend fica em `http://localhost:5173`. O formulário público está em
`/solicitacao` e o login administrativo em `/login`.

### 3. Scripts auxiliares (opcional)

Em `scripts\windows\` (ver Adendo 35.5 do BLUEPRINT):

| Script | O que faz |
|---|---|
| `setup-backend.bat` | Cria a venv, instala dependências, copia `.env.example` → `.env` |
| `setup-frontend.bat` | Roda `npm install` |
| `start-backend.bat` | Ativa a venv e sobe `uvicorn --reload` |
| `start-frontend.bat` | Roda `npm run dev` |
| `start-dev.bat` | Sobe backend e frontend juntos, em janelas separadas |

Esses scripts são um atalho opcional — não substituem os passos manuais
acima, que continuam funcionando sempre.

## Testes

Testes de integração do backend (pytest, contra o MySQL de desenvolvimento
configurado no `.env` — ver Adendo 35.6):

```bat
cd backend
venv\Scripts\activate
pytest
```

## Produção em Linux

Ver seções 19 a 24 do [`BLUEPRINT.md`](docs/BLUEPRINT.md) para a publicação
em Linux com Apache2 (reverse proxy), systemd (Uvicorn/Gunicorn) e o frontend
compilado (`npm run build`) servido como estático. Nunca usar o servidor de
desenvolvimento do Vite nem `uvicorn --reload` em produção.

## Variáveis de ambiente

Ver `backend/.env.example` para a lista completa. Nunca versionar `.env`
real, senhas ou secrets — apenas `.env.example` fica no repositório.
