# Implantação em produção (Linux + Apache2)

Referência: seções 19-25 do [`BLUEPRINT.md`](BLUEPRINT.md). Este guia usa o
domínio fictício `sistema.exemplo.com` e o caminho `/var/www/sistema` — ajuste
para o ambiente real.

```
Internet
  |
Apache2 (HTTPS)
  |
  +-- /      -> React (arquivos estáticos, frontend/dist)
  |
  +-- /api   -> FastAPI (reverse proxy para 127.0.0.1:8000)
  |
 MySQL (local)
```

Nunca usar o servidor de dev do Vite (`npm run dev`) nem `uvicorn --reload`
em produção.

## 1. Usuário e diretórios da aplicação

```bash
sudo useradd --system --home /var/www/sistema --shell /usr/sbin/nologin sistema-medicos
sudo mkdir -p /var/www/sistema/backend /var/www/sistema/frontend
sudo mkdir -p /var/lib/sistema-medicos/uploads
sudo chown -R sistema-medicos:sistema-medicos /var/www/sistema /var/lib/sistema-medicos
```

`/var/lib/sistema-medicos/uploads` é privado — nunca fica dentro de
`frontend/dist` nem em qualquer diretório servido diretamente pelo Apache
(seção 24). O acesso aos documentos é sempre via API autenticada.

## 2. Dependências de sistema

```bash
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip mysql-server \
    apache2 libapache2-mod-proxy-html libmagic1 git
sudo a2enmod proxy proxy_http rewrite headers ssl
```

## 3. Banco de dados

```bash
sudo mysql -e "CREATE DATABASE sistema_medicos CHARACTER SET utf8mb4;"
sudo mysql -e "CREATE USER 'sistema_medicos'@'localhost' IDENTIFIED BY 'SENHA_FORTE_AQUI';"
sudo mysql -e "GRANT ALL PRIVILEGES ON sistema_medicos.* TO 'sistema_medicos'@'localhost';"
```

## 4. Backend

Como o usuário `sistema-medicos` (ou via `sudo -u sistema-medicos`):

```bash
cd /var/www/sistema/backend
git clone <url-do-repositorio> . # ou copiar os arquivos do backend/ para cá
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` com os valores de produção — no mínimo:

```
APP_ENV=production
DATABASE_URL=mysql+pymysql://sistema_medicos:SENHA_FORTE_AQUI@localhost/sistema_medicos
SECRET_KEY=<gerar uma chave aleatoria forte, ex: python -c "import secrets; print(secrets.token_urlsafe(64))">
UPLOAD_DIR=/var/lib/sistema-medicos/uploads
MAX_UPLOAD_SIZE=5242880
SMTP_HOST=...
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
SMTP_FROM=...
FRONTEND_URL=https://sistema.exemplo.com
```

Rode as migrations e crie o administrador inicial:

```bash
venv/bin/alembic upgrade head
venv/bin/python -m scripts.seed_admin --nome "Admin" --email admin@exemplo.com --senha "SenhaForte123!"
```

## 5. Serviço systemd

Crie `/etc/systemd/system/sistema-medicos.service`:

```ini
[Unit]
Description=Sistema de Acesso de Medicos - backend (FastAPI)
After=network.target mysql.service

[Service]
Type=simple
User=sistema-medicos
Group=sistema-medicos
WorkingDirectory=/var/www/sistema/backend
Environment=PATH=/var/www/sistema/backend/venv/bin
ExecStart=/var/www/sistema/backend/venv/bin/gunicorn app.main:app \
    --workers 3 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

O serviço roda como usuário sem privilégios (`sistema-medicos`, sem shell de
login), escuta somente em `127.0.0.1` (nunca exposto direto à internet — o
Apache2 é quem fala com a internet) e reinicia sozinho em caso de falha.

```bash
sudo systemctl daemon-reload
sudo systemctl enable sistema-medicos
sudo systemctl start sistema-medicos
sudo systemctl status sistema-medicos
```

Para atualizar após um deploy: `git pull`, `venv/bin/pip install -r
requirements.txt`, `venv/bin/alembic upgrade head`, depois
`sudo systemctl restart sistema-medicos`.

## 6. Frontend

Em uma máquina com Node.js (pode ser a mesma do servidor ou um passo de CI):

```bash
cd frontend
npm install
npm run build
```

Copie o conteúdo de `frontend/dist/` para `/var/www/sistema/frontend/dist/`
no servidor, com o `SITE_URL`/`VITE_API_URL` de produção configurado em
`frontend/.env.production` antes do build, se aplicável.

## 7. Apache2 — VirtualHost

Crie `/etc/apache2/sites-available/sistema-medicos.conf`:

```apache
<VirtualHost *:443>
    ServerName sistema.exemplo.com

    SSLEngine on
    SSLCertificateFile      /etc/letsencrypt/live/sistema.exemplo.com/fullchain.pem
    SSLCertificateKeyFile   /etc/letsencrypt/live/sistema.exemplo.com/privkey.pem

    DocumentRoot /var/www/sistema/frontend/dist

    # Frontend estatico (React) com suporte ao React Router (secao 20):
    # rotas que nao sao arquivos reais devem cair no index.html.
    <Directory /var/www/sistema/frontend/dist>
        Options -Indexes
        AllowOverride None
        Require all granted
        FallbackResource /index.html
    </Directory>

    # Backend FastAPI via reverse proxy (secao 21/22) - nunca exposto direto.
    ProxyPreserveHost On
    ProxyPass        /api http://127.0.0.1:8000/api
    ProxyPassReverse /api http://127.0.0.1:8000/api

    ErrorLog  ${APACHE_LOG_DIR}/sistema-medicos-error.log
    CustomLog ${APACHE_LOG_DIR}/sistema-medicos-access.log combined
</VirtualHost>

<VirtualHost *:80>
    ServerName sistema.exemplo.com
    Redirect permanent / https://sistema.exemplo.com/
</VirtualHost>
```

```bash
sudo a2ensite sistema-medicos.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

Certificado HTTPS via Let's Encrypt (`certbot --apache -d sistema.exemplo.com`)
antes de habilitar o VirtualHost de produção, ou ajuste os caminhos acima para
um certificado já existente.

## 8. Checklist pós-deploy

- [ ] `systemctl status sistema-medicos` ativo e sem reinícios em loop
- [ ] `curl -s https://sistema.exemplo.com/api/health` retorna `{"status":"ok"}`
- [ ] Formulário público em `/solicitacao` carrega e envia com sucesso
- [ ] Login administrativo funciona e o cookie é `Secure` (verificar no
      DevTools — só é enviado via HTTPS)
- [ ] Refresh em `/admin/dashboard` não dá 404 (confirma o `FallbackResource`)
- [ ] `/var/lib/sistema-medicos/uploads` não é acessível diretamente via URL
      (ex.: `https://sistema.exemplo.com/uploads/...` deve dar 404)
- [ ] Backup do MySQL configurado (fora do escopo deste documento)
