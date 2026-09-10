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

Passo a passo da instalação padrão (Ubuntu/Debian, domínio real + Certbot).
Guia completo com alternativas — sem domínio ainda (certificado
autoassinado), atualização de um deploy existente, checklist pós-deploy — em
[`docs/DEPLOY_LINUX.md`](docs/DEPLOY_LINUX.md); especificação de referência
nas seções 19 a 25 do [`BLUEPRINT.md`](docs/BLUEPRINT.md). Nunca usar o
servidor de desenvolvimento do Vite nem `uvicorn --reload` em produção.
Troque `sistema.exemplo.com` e `/var/www/sistema` pelos valores reais do seu
servidor.

### 1. Dependências de sistema

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip \
    mysql-server \
    apache2 libapache2-mod-proxy-html libmagic1 \
    git \
    certbot python3-certbot-apache
sudo a2enmod proxy proxy_http rewrite headers ssl

curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. Usuário e diretórios da aplicação

```bash
sudo useradd --system --home /var/www/sistema --shell /usr/sbin/nologin sistema-medicos
sudo mkdir -p /var/www/sistema/backend /var/www/sistema/frontend
sudo mkdir -p /var/lib/sistema-medicos/uploads
sudo chown -R sistema-medicos:sistema-medicos /var/www/sistema /var/lib/sistema-medicos
```

### 3. Banco de dados MySQL

```bash
sudo mysql -e "CREATE DATABASE sistema_medicos CHARACTER SET utf8mb4;"
sudo mysql -e "CREATE USER 'sistema_medicos'@'localhost' IDENTIFIED BY 'SENHA_FORTE_AQUI';"
sudo mysql -e "GRANT ALL PRIVILEGES ON sistema_medicos.* TO 'sistema_medicos'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"
```

### 4. Backend

```bash
cd /var/www/sistema/backend
git clone <url-do-repositorio> .   # ou copiar os arquivos do backend/ para cá
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` com os valores de produção (`DATABASE_URL`, `SECRET_KEY`,
`UPLOAD_DIR=/var/lib/sistema-medicos/uploads`, etc.):

```
APP_ENV=production
DATABASE_URL=mysql+pymysql://sistema_medicos:SENHA_FORTE_AQUI@localhost/sistema_medicos
SECRET_KEY=<gerar: python -c "import secrets; print(secrets.token_urlsafe(64))">
ACCESS_TOKEN_EXPIRE_MINUTES=480
UPLOAD_DIR=/var/lib/sistema-medicos/uploads
MAX_UPLOAD_SIZE=5242880
FRONTEND_URL=https://sistema.exemplo.com
```

> ⚠️ **`FRONTEND_URL` precisa ser a URL pública real, nunca o valor de
> dev/exemplo.** Esquecido como `localhost:5173`, o CORS bloqueia o login
> silenciosamente — o sintoma é "credenciais inválidas" mesmo com senha
> certa (Adendo 35.16 do BLUEPRINT).

Migrations e administrador inicial:

```bash
venv/bin/alembic upgrade head
venv/bin/python -m scripts.seed_admin --nome "Admin" --login admin --email admin@exemplo.com --senha "SenhaForte123!"
```

### 5. Frontend

```bash
cd frontend
echo "VITE_API_URL=https://sistema.exemplo.com/api" > .env.production
npm install
npm run build
```

> ⚠️ **`VITE_API_URL` não é opcional em produção.** Sem ele, o frontend
> tenta falar direto com a porta 8000 do backend, que não fica exposta
> atrás do Apache2 — o sintoma é `ERR_CONNECTION_TIMED_OUT` + aviso de
> "Mixed Content" no navegador (Adendo 35.16 do BLUEPRINT). Aponte sempre
> para o proxy `/api` do Apache2, nunca para a porta 8000.

Copie `frontend/dist/` para `/var/www/sistema/frontend/dist/` no servidor
(`rsync`, `scp` ou build direto no servidor).

### 6. Serviço systemd

Crie `/etc/systemd/system/sistema-medicos.service` (modelo completo em
`docs/DEPLOY_LINUX.md`, seção 6) e habilite:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sistema-medicos
sudo systemctl start sistema-medicos
sudo systemctl status sistema-medicos
```

### 7. Apache2 — VirtualHost e HTTPS

Crie o VirtualHost em `/etc/apache2/sites-available/sistema-medicos.conf`
(modelo completo, com proxy `/api` e `FallbackResource` para o React
Router, em `docs/DEPLOY_LINUX.md`, seção 7), habilite e emita o
certificado:

```bash
sudo a2ensite sistema-medicos.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
sudo certbot --apache -d sistema.exemplo.com
```

Sem domínio real ainda? Use a alternativa de certificado autoassinado
documentada em `docs/DEPLOY_LINUX.md` (seção 7.3) — é temporária, com
aviso de navegador não confiável, até haver domínio para o Certbot.

### 8. Verificação final

```bash
sudo systemctl status sistema-medicos
sudo journalctl -u sistema-medicos -f
curl -s https://sistema.exemplo.com/api/health
```

Deve retornar `{"status":"ok"}`. Checklist completo (login, upload
autenticado, SMTP, renovação de certificado) em `docs/DEPLOY_LINUX.md`,
seção 8.

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
