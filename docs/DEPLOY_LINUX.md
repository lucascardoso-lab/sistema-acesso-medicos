# Implantação em produção (Linux + Apache2)

Referência: seções 19-25 do [`BLUEPRINT.md`](BLUEPRINT.md) (e os adendos da
seção 35, que atualizam decisões tomadas depois da especificação original —
em especial o Adendo 35.12, que mudou a configuração de SMTP). Este guia
parte de um servidor Ubuntu/Debian limpo e usa o domínio fictício
`sistema.exemplo.com` e o caminho `/var/www/sistema` — troque pelos valores
reais do seu ambiente em todos os passos abaixo.

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

## 1. Pré-requisitos de sistema operacional

Atualize o sistema:

```bash
sudo apt update && sudo apt upgrade -y
```

Instale as dependências de sistema necessárias — Python, MySQL, Apache2 e
módulos, `libmagic1` (usado pelo `python-magic` na validação de upload,
Adendo 35.3), Git e Certbot:

```bash
sudo apt install -y python3 python3-venv python3-pip \
    mysql-server \
    apache2 libapache2-mod-proxy-html libmagic1 \
    git \
    certbot python3-certbot-apache
sudo a2enmod proxy proxy_http rewrite headers ssl
```

Confirme que o Python é 3.11 ou mais recente (`python3 --version`); em
distribuições mais antigas pode ser necessário um PPA/backport.

Node.js (para o build do frontend, seção 5) — o pacote `nodejs` dos
repositórios padrão do Ubuntu/Debian costuma estar desatualizado. Instale a
versão LTS a partir do repositório oficial NodeSource:

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs
node --version   # confirme LTS (18+)
```

Se o build do frontend for feito em outra máquina (ex.: pipeline de CI),
este passo do Node.js pode ser pulado no servidor — só é necessário onde o
`npm run build` for executado.

## 2. Usuário e diretórios da aplicação

```bash
sudo useradd --system --home /var/www/sistema --shell /usr/sbin/nologin sistema-medicos
sudo mkdir -p /var/www/sistema/backend /var/www/sistema/frontend
sudo mkdir -p /var/lib/sistema-medicos/uploads
sudo chown -R sistema-medicos:sistema-medicos /var/www/sistema /var/lib/sistema-medicos
```

`/var/lib/sistema-medicos/uploads` é privado — nunca fica dentro de
`frontend/dist` nem em qualquer diretório servido diretamente pelo Apache
(seção 24 do BLUEPRINT). O acesso aos documentos é sempre via API
autenticada. Esse caminho é o valor de `UPLOAD_DIR` usado no `.env` do
backend (passo 4).

## 3. Banco de dados MySQL

```bash
sudo mysql -e "CREATE DATABASE sistema_medicos CHARACTER SET utf8mb4;"
sudo mysql -e "CREATE USER 'sistema_medicos'@'localhost' IDENTIFIED BY 'SENHA_FORTE_AQUI';"
sudo mysql -e "GRANT ALL PRIVILEGES ON sistema_medicos.* TO 'sistema_medicos'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"
```

Troque `SENHA_FORTE_AQUI` por uma senha forte gerada na hora — ela vai para
o `DATABASE_URL` do `.env` de produção (passo 4).

**Backup do MySQL não é coberto por este guia.** É responsabilidade do time
de infraestrutura configurar backup periódico (ex.: `mysqldump` agendado ou
solução gerenciada do provedor) antes de colocar o sistema em uso real —
os dados armazenados incluem cadastro de médicos e histórico de decisões
de acesso.

## 4. Backend

Como o usuário `sistema-medicos` (ou via `sudo -u sistema-medicos`):

```bash
cd /var/www/sistema/backend
git clone <url-do-repositorio> . # ou copiar os arquivos do backend/ para cá
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` com os valores de produção. Esta é a lista completa das
variáveis usadas hoje pelo backend (confira sempre contra
`backend/.env.example`, que é a fonte de verdade — SMTP não faz mais parte
desta lista desde o Adendo 35.12, veja a nota abaixo):

```
APP_ENV=production
DATABASE_URL=mysql+pymysql://sistema_medicos:SENHA_FORTE_AQUI@localhost/sistema_medicos
SECRET_KEY=<gerar uma chave aleatoria forte, ex: python -c "import secrets; print(secrets.token_urlsafe(64))">
ACCESS_TOKEN_EXPIRE_MINUTES=480
UPLOAD_DIR=/var/lib/sistema-medicos/uploads
MAX_UPLOAD_SIZE=5242880
FRONTEND_URL=https://sistema.exemplo.com
```

> **SMTP não é configurado aqui.** Desde o Adendo 35.12, o servidor de
> e-mail (host/porta/usuário/senha/remetente) é cadastrado pelo
> administrador na tela "Configurações" da área administrativa, depois do
> primeiro login — a senha fica armazenada criptografada no banco, nunca em
> texto puro nem em variável de ambiente. Não esqueça desse passo pós-deploy
> (checklist, item 8).

Rode as migrations e crie o administrador inicial:

```bash
venv/bin/alembic upgrade head
venv/bin/python -m scripts.seed_admin --nome "Admin" --login admin --email admin@exemplo.com --senha "SenhaForte123!"
```

## 5. Frontend

Em uma máquina com Node.js (pode ser a mesma do servidor ou um passo de
build separado, ex. CI):

```bash
cd frontend
echo "VITE_API_URL=https://sistema.exemplo.com/api" > .env.production
npm install
npm run build
```

`VITE_API_URL` fixa a URL da API usada pelo frontend compilado — em
desenvolvimento essa variável é opcional (o cliente deduz a URL a partir do
`hostname` acessado, Adendo 35.9), mas em produção é recomendável defini-la
explicitamente para apontar sempre ao domínio público real.

Copie o conteúdo gerado em `frontend/dist/` para
`/var/www/sistema/frontend/dist/` no servidor:

```bash
rsync -av --delete frontend/dist/ sistema-medicos@servidor:/var/www/sistema/frontend/dist/
```

(ou `scp -r`, `git pull` + build direto no servidor, conforme seu processo
de deploy).

## 6. Serviço systemd

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

Para acompanhar os logs em tempo real (útil para diagnosticar falha no
start ou erro 502 do Apache):

```bash
sudo journalctl -u sistema-medicos -f
```

Para atualizar após um deploy: `git pull`, `venv/bin/pip install -r
requirements.txt`, `venv/bin/alembic upgrade head`, depois
`sudo systemctl restart sistema-medicos`.

## 7. Apache2 — VirtualHost e HTTPS

### 7.1. VirtualHost HTTP (porta 80) — necessário antes do Certbot

O Certbot precisa conseguir acessar o domínio por HTTP para validar que
você controla o servidor, então crie primeiro um VirtualHost **sem SSL**.
Crie `/etc/apache2/sites-available/sistema-medicos.conf`:

```apache
<VirtualHost *:80>
    ServerName sistema.exemplo.com

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
```

Habilite o site e recarregue o Apache2:

```bash
sudo a2ensite sistema-medicos.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

Nesse ponto o site já deve responder em `http://sistema.exemplo.com`
(sem HTTPS ainda) — confirme antes de seguir para o Certbot.

### 7.2. Certificado HTTPS com Certbot

Com o DNS do domínio já apontando para o servidor e o VirtualHost HTTP no
ar, rode o Certbot em modo interativo:

```bash
sudo certbot --apache -d sistema.exemplo.com
```

O Certbot valida o domínio, obtém o certificado Let's Encrypt, edita
automaticamente o VirtualHost para adicionar `SSLEngine on` e os caminhos
do certificado, e oferece a opção de criar o redirecionamento automático de
HTTP (porta 80) para HTTPS (porta 443) — responda "sim" a essa opção.

**Alternativa manual:** se o domínio já tem um VirtualHost customizado que
não deve ser reescrito automaticamente pelo Certbot, use
`sudo certbot certonly --apache -d sistema.exemplo.com` (só emite o
certificado, sem tocar na configuração do Apache) e edite o VirtualHost
você mesmo, apontando para os arquivos gerados em
`/etc/letsencrypt/live/sistema.exemplo.com/`.

Depois de rodar o Certbot, o VirtualHost final deve ficar equivalente a
isto (é o que o modo automático gera):

```apache
<VirtualHost *:443>
    ServerName sistema.exemplo.com

    SSLEngine on
    SSLCertificateFile      /etc/letsencrypt/live/sistema.exemplo.com/fullchain.pem
    SSLCertificateKeyFile   /etc/letsencrypt/live/sistema.exemplo.com/privkey.pem

    DocumentRoot /var/www/sistema/frontend/dist

    <Directory /var/www/sistema/frontend/dist>
        Options -Indexes
        AllowOverride None
        Require all granted
        FallbackResource /index.html
    </Directory>

    ProxyPreserveHost On
    ProxyPass        /api http://127.0.0.1:8000/api
    ProxyPassReverse /api http://127.0.0.1:8000/api

    ErrorLog  ${APACHE_LOG_DIR}/sistema-medicos-error.log
    CustomLog ${APACHE_LOG_DIR}/sistema-medicos-access.log combined
</VirtualHost>

<VirtualHost *:80>
    ServerName sistema.exemplo.com
    RewriteEngine on
    RewriteCond %{SERVER_NAME} =sistema.exemplo.com
    RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>
```

### 7.3. Renovação automática

O pacote `certbot` instala um timer systemd que renova certificados perto
do vencimento automaticamente. Confirme que está ativo e teste a renovação
sem aplicar de fato:

```bash
sudo systemctl status certbot.timer
sudo certbot renew --dry-run
```

Se o `--dry-run` terminar sem erro, a renovação automática está configurada
corretamente.

## 8. Checklist pós-deploy

- [ ] `systemctl status sistema-medicos` ativo e sem reinícios em loop
- [ ] `curl -s https://sistema.exemplo.com/api/health` retorna `{"status":"ok"}`
- [ ] Formulário público em `/solicitacao` carrega e envia com sucesso
- [ ] Login administrativo funciona e o cookie é `Secure` (verificar no
      DevTools — só é enviado via HTTPS)
- [ ] Refresh em `/admin/dashboard` não dá 404 (confirma o `FallbackResource`)
- [ ] Documento e foto de uma solicitação abrem normalmente autenticado
      (`/admin/solicitacoes/{id}`, links "Ver documento"/"Ver foto") e dão
      401/404 sem login
- [ ] `/var/lib/sistema-medicos/uploads` não é acessível diretamente via URL
      (ex.: `https://sistema.exemplo.com/uploads/...` deve dar 404)
- [ ] SMTP configurado pela tela "Configurações" (Adendo 35.12) e testado
      com o botão "Enviar e-mail de teste"
- [ ] `certbot renew --dry-run` sem erro (renovação automática do certificado)
- [ ] Backup do MySQL configurado (fora do escopo deste documento)
