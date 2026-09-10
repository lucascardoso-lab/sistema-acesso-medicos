# Sistema de Cadastro, Validação e Liberação de Acesso de Médicos

Sistema web para cadastro, validação e liberação de acesso de médicos. O
médico acessa uma página pública, preenche seus dados profissionais e envia
documentos para comprovação de identidade. Um técnico de TI acessa a área
administrativa, analisa a solicitação e, após aprovar ou rejeitar, envia ao
médico o resultado da análise (e, em caso de aprovação, as credenciais de
acesso ao sistema de resultados).

A especificação funcional e técnica completa está em
[`docs/BLUEPRINT.md`](docs/BLUEPRINT.md), incluindo o histórico de decisões
técnicas tomadas ao longo do desenvolvimento (seção 35).

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
python -m scripts.seed_admin --nome "Seu Nome" --login admin --email admin@exemplo.com --senha "SenhaForte123!"
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

Guia completo de implantação em [`docs/DEPLOY_LINUX.md`](docs/DEPLOY_LINUX.md):
usuário/diretórios da aplicação, MySQL, virtualenv, serviço systemd
(Gunicorn + Uvicorn workers), VirtualHost do Apache2 (reverse proxy + React
Router) e checklist pós-deploy. Especificação de referência nas seções 19 a
25 do [`BLUEPRINT.md`](docs/BLUEPRINT.md). Nunca usar o servidor de
desenvolvimento do Vite nem `uvicorn --reload` em produção.

## Variáveis de ambiente

Ver `backend/.env.example` (backend) e `frontend/.env.example` (frontend)
para a lista completa. Nunca versionar `.env` real, senhas ou secrets —
apenas os `.env.example` ficam no repositório. A configuração de SMTP não é
feita por variável de ambiente: é cadastrada pelo administrador na tela
"Configurações" da área administrativa (senha armazenada criptografada no
banco — ver Adendo 35.12 do BLUEPRINT).

## Uso

Software de uso interno da INGOH (Instituto Goiano de Oncologia e
Hematologia). Não possui licença de código aberto.
