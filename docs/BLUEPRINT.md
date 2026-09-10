# BLUEPRINT — Sistema de Cadastro, Validação e Liberação de Acesso de Médicos

Este documento é a fonte única de verdade da especificação funcional e técnica do
projeto. Toda decisão técnica relevante tomada durante o desenvolvimento (inclusive
as não previstas originalmente) deve ser registrada como um **adendo** na seção
"Histórico de decisões / Adendos", ao final deste arquivo, seguindo numeração
sequencial (10.1, 10.2, ...).

---

## Índice

1. Objetivo do sistema
2. Fluxo principal
3. Formulário público
4. Status das solicitações
5. Área administrativa
6. Filtros
7. Tela de análise
8. Ações do técnico
9. Histórico / auditoria
10. Dashboard
11. Usuários administrativos
12. Segurança
13. LGPD
14. Banco de dados MySQL
15. Backend
16. Frontend
17. Desenvolvimento no Windows
18. Scripts para facilitar o desenvolvimento no Windows
19. Produção em Linux
20. Publicação do frontend
21. Publicação do backend
22. Apache2
23. Serviço systemd
24. Arquivos enviados em produção
25. Configuração através de ambiente
26. Envio de e-mail
27. WhatsApp
28. Credenciais do médico
29. Compatibilidade Windows/Linux
30. Estrutura raiz
31. .gitignore
32. README
33. Desenvolvimento incremental
34. Regras de implementação
35. Histórico de decisões / Adendos

---

## Contexto geral

Sistema web simples para cadastro, validação e liberação de acesso de médicos.

- Desenvolvido e validado inicialmente em ambiente **Windows, sem Docker**.
- Posteriormente publicado em servidor **Linux com Apache2**.
- Projeto deve funcionar corretamente nos dois ambientes desde o início.

### Stack obrigatória

**Frontend:** React, Vite, TypeScript

**Backend:** Python, FastAPI, SQLAlchemy, Pydantic, Alembic

**Banco de dados:** MySQL

**Ambientes:**

| | Desenvolvimento | Produção |
|---|---|---|
| SO | Windows | Linux |
| Execução | Local, sem Docker | Apache2 + systemd |
| Backend | `uvicorn --reload` | Uvicorn/Gunicorn como serviço |
| Frontend | Vite dev server | Build estático (`dist`) servido pelo Apache2 |
| Banco | MySQL local | MySQL |

---

## 1. Objetivo do sistema

O sistema recebe solicitações de acesso de médicos. O médico acessa uma página
pública, preenche seus dados profissionais e envia documentos para comprovação de
identidade. Um técnico de TI acessa uma área administrativa, analisa as
solicitações recebidas e, após aprovação, informa ao médico as credenciais para
acesso ao sistema de resultados.

---

## 2. Fluxo principal

1. Médico acessa o formulário público.
2. Preenche seus dados.
3. Anexa seu documento de identificação.
4. Anexa uma foto segurando o documento.
5. Envia a solicitação.
6. Sistema gera um protocolo.
7. Solicitação fica com status "Pendente".
8. Técnico de TI entra no painel administrativo.
9. Técnico analisa os documentos.
10. Técnico aprova ou rejeita.
11. Em caso de aprovação, registra os dados de acesso.
12. Técnico envia a resposta ao médico.
13. Sistema registra que a solicitação foi respondida.

---

## 3. Formulário público

Campos:

- Nome completo
- Conselho profissional (ex: CRM)
- Número do conselho
- UF do conselho
- Especialidade
- E-mail
- Telefone / WhatsApp

**Uploads obrigatórios:**

- **Documento de identificação** — aceita PDF, JPG, JPEG, PNG (ex: CNH, CNH
  Digital, ou outro documento permitido pela instituição).
- **Foto segurando o documento** — aceita JPG, JPEG, PNG.

**Validações:**

- Validação dos campos
- Validação de tamanho máximo de arquivo
- Validação de extensão
- Validação de MIME type no backend
- Indicador visual do upload
- Checkbox de consentimento para tratamento dos dados pessoais

Após o envio: mensagem "Solicitação enviada com sucesso." + protocolo único
(ex: `SOL-2026-000001`).

---

## 4. Status das solicitações

- Pendente
- Em análise
- Aprovada
- Rejeitada
- Respondida

Registrar: data da solicitação, data da última atualização, técnico responsável,
data de início da análise, data de aprovação/rejeição, data da resposta.

---

## 5. Área administrativa

Autenticação obrigatória. Rotas:

- `/login`
- `/admin/dashboard`
- `/admin/solicitacoes`
- `/admin/solicitacoes/:id`

Tabela de solicitações com: Protocolo, Nome, Conselho, Número do conselho,
Especialidade, E-mail, Telefone, Data, Status, Técnico responsável, Ações.
Com paginação.

---

## 6. Filtros

Por Status, Nome, Número do conselho, Conselho, Especialidade, Data inicial,
Data final. Mais busca textual.

---

## 7. Tela de análise

**Dados pessoais:** Nome, E-mail, Telefone

**Dados profissionais:** Conselho, UF, Número do conselho, Especialidade

**Documentos:** visualização segura do documento enviado e da foto segurando o
documento.

⚠️ Os arquivos **não** ficam disponíveis diretamente por pasta pública do Apache.
O backend verifica autenticação antes de fornecer acesso aos arquivos.

---

## 8. Ações do técnico

- Iniciar análise
- Aprovar
- Rejeitar
- Adicionar observações internas
- Informar motivo da rejeição
- Registrar dados de acesso
- Marcar solicitação como respondida

Toda mudança importante gera registro de histórico.

---

## 9. Histórico / auditoria

Registrar por evento: Solicitação, Usuário responsável, Ação, Status anterior,
Novo status, Data, Hora, Observação.

Exemplos de eventos: "Solicitação criada", "Análise iniciada", "Solicitação
aprovada", "Solicitação rejeitada", "Credenciais enviadas por e-mail",
"Solicitação marcada como respondida".

---

## 10. Dashboard

Cards: Total de solicitações, Recebidas hoje, Pendentes, Em análise, Aprovadas,
Rejeitadas, Respondidas.

Gráficos: solicitações recebidas nos últimos 30 dias; distribuição por status.

---

## 11. Usuários administrativos

Perfis iniciais: **Administrador** e **Técnico**.

- Administrador: gerencia usuários, consulta todas as solicitações, altera
  configurações.
- Técnico: consulta solicitações, analisa, aprova/rejeita, registra resposta.

---

## 12. Segurança

- Senhas administrativas com hash seguro (nunca texto puro)
- Autenticação segura, controle de sessão/token, autorização por perfil
- Rate limiting no formulário público
- Validação de upload no backend, limite de tamanho de arquivos
- Nome aleatório para arquivos enviados (nunca confiar no nome original)
- Nunca permitir execução de arquivos enviados
- Documentos fora da pasta pública do frontend, nunca em `/public`
- Não expor caminhos físicos dos arquivos; acesso somente via API protegida
- Não registrar dados sensíveis em logs
- Variáveis de ambiente para configuração sensível
- HTTPS em produção, CORS configurado adequadamente
- Auditoria das operações

---

## 13. LGPD

Dados armazenados: Nome, Telefone, E-mail, Dados profissionais, Documento de
identificação, Fotografia.

Checkbox obrigatório no formulário:

> "Declaro estar ciente e autorizo o tratamento dos dados pessoais e documentos
> enviados exclusivamente para finalidade de validação e liberação de acesso."

Registrar data/hora do consentimento e versão do termo aceito. Preparar estrutura
para, futuramente, implementar política automática de retenção/exclusão dos
documentos.

---

## 14. Banco de dados MySQL

Migrations via Alembic.

**`users`**: id, nome, email, password_hash, perfil, ativo, created_at, updated_at

**`solicitacoes`**: id, protocolo, nome_completo, conselho, numero_conselho,
uf_conselho, especialidade, email, telefone, documento_path,
selfie_documento_path, status, observacao_interna, motivo_rejeicao,
responsavel_id, consentimento_lgpd, consentimento_versao, consentimento_at,
created_at, updated_at, analise_iniciada_at, analisado_at, respondido_at

**`historico_solicitacoes`**: id, solicitacao_id, usuario_id, acao,
status_anterior, status_novo, descricao, created_at

**`comunicacoes`**: id, solicitacao_id, canal, destinatario, status_envio,
enviado_por, enviado_at, erro

Criar primary keys, foreign keys, índices, constraints e relacionamentos.

---

## 15. Backend

API REST em FastAPI. Estrutura sugerida:

```
backend/
  app/
    main.py
    api/
    models/
    schemas/
    services/
    repositories/
    auth/
    database/
    utils/
    core/
  migrations/
  uploads/
  requirements.txt
  alembic.ini
  .env.example
```

Uploads **fora** da pasta pública do frontend.

Endpoints: Login, Logout, Usuário autenticado, Criar solicitação, Upload de
documentos, Listar solicitações, Visualizar solicitação, Visualizar arquivo
protegido, Atualizar solicitação, Iniciar análise, Aprovar, Rejeitar, Registrar
resposta, Dashboard, Histórico, Usuários administrativos.

---

## 16. Frontend

```
frontend/
  src/
    components/
    pages/
    layouts/
    services/
    hooks/
    contexts/
    types/
    utils/
```

**Páginas públicas:** `/solicitacao`, `/solicitacao/sucesso`

**Páginas administrativas:** `/login`, `/admin/dashboard`, `/admin/solicitacoes`,
`/admin/solicitacoes/:id`, `/admin/usuarios`

**Componentes reutilizáveis:** Input, Select, Upload, Modal, Button, Card, Badge,
Table, Pagination, Loading, Alert, ConfirmDialog.

---

## 17. Desenvolvimento no Windows

Sem Docker. README com instruções detalhadas.

Backend:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:
```
npm install
npm run dev
```

Banco: MySQL local no Windows, conexão via variável de ambiente:
```
DATABASE_URL=mysql+pymysql://usuario:senha@localhost/nome_banco
```

Criar `.env.example`. Nunca versionar senha real.

---

## 18. Scripts para facilitar o desenvolvimento no Windows

Opcional: `start-backend.bat`, `start-frontend.bat` ou `start-dev.bat`. Não são
dependência obrigatória — documentar também os comandos manualmente no README.

---

## 19. Produção em Linux

Apache2, MySQL, Python, virtualenv, systemd, Uvicorn ou Gunicorn + Uvicorn
Workers, React compilado.

Nunca usar o servidor de dev do Vite nem `uvicorn --reload` em produção.

---

## 20. Publicação do frontend

`npm run build` gera `frontend/dist`, servido pelo Apache2 (ex:
`/var/www/sistema/frontend/dist`).

Configurar suporte ao React Router: rotas que não representam arquivos reais
devem redirecionar para `index.html` (evita 404 em `/admin/dashboard`,
`/admin/solicitacoes` etc. ao dar refresh).

---

## 21. Publicação do backend

Ex: `/var/www/sistema/backend`, virtualenv em
`/var/www/sistema/backend/venv`. API local em `127.0.0.1:8000`, nunca exposta
diretamente à internet — Apache2 atua como reverse proxy.

---

## 22. Apache2

```
Internet
  |
Apache2
  |
  +-- /      -> React (arquivos estáticos)
  |
  +-- /api   -> FastAPI (reverse proxy)
  |
 MySQL
```

Exemplo (domínio fictício `sistema.exemplo.com`):
- `https://sistema.exemplo.com/` → Frontend React
- `https://sistema.exemplo.com/api/` → Backend FastAPI

Módulos Apache necessários: `mod_proxy`, `mod_proxy_http`, `mod_rewrite`,
`headers`. SSL em produção. Criar exemplo de VirtualHost.

---

## 23. Serviço systemd

Exemplo conceitual: `sistema-medicos.service`. O serviço deve:

- Iniciar automaticamente com o Linux
- Reiniciar em caso de falha
- Executar com usuário sem privilégios excessivos (nunca root)
- Usar o virtualenv da aplicação
- Executar o backend localmente

Documentar `systemctl start/stop/restart/status/enable`.

---

## 24. Arquivos enviados em produção

Não ficam disponíveis diretamente pelo Apache. Sugestão:
`/var/lib/sistema-medicos/uploads/` (ou outra pasta privada). Acesso somente via
backend, após autenticação.

Configurável via `UPLOAD_DIR`:
- Windows: `UPLOAD_DIR=C:\sistema-medicos\uploads`
- Linux: `UPLOAD_DIR=/var/lib/sistema-medicos/uploads`

Nunca hardcode caminhos — usar `pathlib` para manipulação multiplataforma.

---

## 25. Configuração através de ambiente

`.env.example`:

```
APP_ENV=development
DATABASE_URL=
SECRET_KEY=
UPLOAD_DIR=
MAX_UPLOAD_SIZE=
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
FRONTEND_URL=
```

Valores diferentes entre desenvolvimento e produção.

---

## 26. Envio de e-mail

SMTP, sem credenciais no código. Ação do técnico: "Enviar resposta". Registrar
destinatário, data, status, técnico, possível erro.

Se o SMTP falhar: não marcar automaticamente como respondida, informar erro ao
técnico, permitir nova tentativa.

---

## 27. WhatsApp

Integração automática não é obrigatória no MVP. Preparar apenas estrutura para
futuramente suportar WhatsApp Business API / Meta WhatsApp Cloud API / outro
provedor.

No MVP: ação "Copiar mensagem para WhatsApp", que gera mensagem padronizada para
o técnico copiar e enviar manualmente.

---

## 28. Credenciais do médico

Evitar senha permanente em texto puro. Arquitetura ideal: gerar usuário, gerar
token temporário, enviar link de ativação, médico define sua própria senha.

Se não for viável no MVP, documentar claramente a limitação e deixar a
arquitetura preparada para essa evolução. Nunca registrar senha em logs.

---

## 29. Compatibilidade Windows/Linux

Evitar caminhos hardcoded, barras manuais, dependências específicas de SO sem
necessidade. Usar `pathlib` e configuração via variáveis de ambiente.

---

## 30. Estrutura raiz

```
sistema-medicos/
  backend/
  frontend/
  docs/
  scripts/
  README.md
  .gitignore
```

Sem Dockerfile, sem docker-compose.yml — Docker não é requisito.

---

## 31. .gitignore

Ignorar: `.env`, `venv/`, `__pycache__/`, `node_modules/`, `frontend/dist/`,
`uploads/`, `*.log`, arquivos temporários.

Nunca versionar: documentos enviados, senhas, secrets, banco de dados, `.env`
reais.

---

## 32. README

**Desenvolvimento Windows:** pré-requisitos, instalação Python, virtualenv,
dependências, instalação/configuração MySQL, criação do banco, `.env`,
migrations, execução backend/frontend, criação do primeiro administrador.

**Produção Linux:** instalação de pacotes, usuário Linux da aplicação,
diretório, virtualenv, dependências Python, MySQL, variáveis de ambiente,
Alembic, build do React, permissões, uploads, systemd, Apache2, reverse proxy,
HTTPS, reinicialização dos serviços.

---

## 33. Desenvolvimento incremental

Ordem de implementação:

1. Analisar requisitos
2. Definir arquitetura
3. Criar estrutura de diretórios
4. Criar banco/modelos
5. Configurar Alembic
6. Criar autenticação
7. Criar API
8. Criar upload seguro
9. Criar frontend público
10. Criar login administrativo
11. Criar dashboard
12. Criar listagem de solicitações
13. Criar tela de análise
14. Criar histórico
15. Criar envio de e-mail
16. Criar gerenciamento básico de usuários
17. Criar scripts auxiliares Windows
18. Testar integração frontend/backend
19. Criar documentação para Windows
20. Criar documentação de implantação Linux + Apache2

Antes de cada etapa importante, explicar brevemente o que será feito e depois
implementar. Não parar apenas na estrutura inicial — continuar até termos uma
primeira versão funcional do MVP.

---

## 34. Regras de implementação

- Não utilizar Docker
- Desenvolvimento e testes inicialmente no Windows; produção posteriormente em Linux
- Apache2 como servidor web/reverse proxy
- MySQL nos dois ambientes — não usar SQLite
- Não usar dados hardcoded como solução definitiva
- Tratamento adequado de erros
- Validações no frontend e no backend
- API com prefixo `/api`
- Documentação automática do FastAPI
- Migrations obrigatórias
- Não armazenar secrets no código
- Código simples e organizado — evitar overengineering
- Priorizar um MVP funcional, preparado para crescer
- Compatibilidade Windows/Linux mantida
- Caminhos configuráveis via variáveis de ambiente
- Todos os documentos enviados permanecem privados

Ao tomar decisões técnicas não especificadas aqui, escolher a solução mais
simples, segura e fácil de manter, e registrar a decisão como adendo neste
arquivo.

---

## 35. Histórico de decisões / Adendos

> Registrar aqui toda decisão técnica tomada durante o desenvolvimento que não
> estava explicitamente definida acima, bugs relevantes encontrados/corrigidos, e
> mudanças de escopo. Formato sugerido:
>
> **Adendo X.Y — título curto**
> Contexto, decisão tomada, motivo, arquivos afetados.

**Adendo 35.1 — Sessão administrativa via cookie httpOnly**

Contexto: o BLUEPRINT não especifica como o token de autenticação da área
administrativa deve ser transportado entre frontend e backend (§5, §12).

Decisão: o backend emite um JWT e o envia em um cookie `httpOnly` + `Secure`
(em produção) + `SameSite=Lax`, em vez de retornar o token no corpo da
resposta para ser guardado em `localStorage`. O frontend (`axios`) usa
`withCredentials: true` em todas as chamadas e trata `401` redirecionando para
`/login`. Proteção CSRF será resolvida por um header customizado somado a
`SameSite=Lax` quando os endpoints de mutação forem implementados (etapa 6).

Motivo: cookie `httpOnly` não é acessível via JavaScript, reduzindo a
superfície de roubo de token por XSS — mais seguro que `localStorage`, que
fica exposto a qualquer script injetado na página. É a opção mais simples que
atende à exigência de "autenticação segura, controle de sessão/token" do §12
sem introduzir refresh tokens ou infraestrutura adicional no MVP.

Arquivos afetados: `frontend/src/services/api.ts` (cliente axios com
`withCredentials: true`), `frontend/src/contexts/AuthContext.tsx`. O emissor
do cookie no backend (`/api/auth/login`) será implementado na etapa 6
(autenticação).

**Adendo 35.2 — API de solicitações: autorização, transições de status e paths de arquivo**

Contexto: o §11 descreve os perfis Administrador e Técnico de forma narrativa
("Administrador: gerencia usuários, consulta... Técnico: consulta, analisa,
aprova/rejeita, registra resposta"), sem deixar explícito se o Administrador
também pode executar as ações de análise (iniciar análise, aprovar, rejeitar,
marcar respondida), nem qual a ordem obrigatória entre essas ações.

Decisão:
1. Os endpoints de leitura e ação de `/api/solicitacoes/*` exigem apenas
   autenticação válida (`get_current_user`), sem restrição adicional por
   perfil — Administrador tem acesso pleno às mesmas ações do Técnico, por
   ser o perfil de maior privilégio.
2. Máquina de estados aplicada no `solicitacao_service`: `iniciar_analise`
   exige status `pendente`; `aprovar`/`rejeitar` exigem `em_analise`;
   `marcar_respondida` exige `aprovada` ou `rejeitada`. Transição fora de
   ordem retorna HTTP 409 com o status atual e o esperado.
3. `documento_path` e `selfie_documento_path` do model `Solicitacao` nunca
   aparecem nos schemas de resposta (`SolicitacaoListItem`/`SolicitacaoDetail`)
   — nenhum path físico é exposto pela API, conforme §12. A visualização
   seguro dos arquivos será implementada como endpoint dedicado na etapa 8
   (upload seguro).

Motivo: opção mais simples e segura para o MVP — evita duplicar lógica de
autorização por ação antes de haver um caso de uso real que exija Técnico e
Administrador terem permissões diferentes, e mantém a auditoria (histórico)
consistente ao impedir pular etapas do fluxo de análise.

Arquivos afetados: `backend/app/api/routes/solicitacoes.py`,
`backend/app/services/solicitacao_service.py`,
`backend/app/schemas/solicitacao.py`.

**Adendo 35.3 — Upload seguro: validação, armazenamento e visualização de documentos**

Contexto: o BLUEPRINT (§3, §12) exige validação de tamanho/extensão/MIME type,
nome de arquivo aleatório e acesso aos documentos somente via API autenticada,
sem detalhar o mecanismo exato.

Decisão:
1. Validação em duas camadas por upload: extensão do nome do arquivo (allowlist
   por campo — documento aceita `.pdf/.jpg/.jpeg/.png`, foto aceita apenas
   `.jpg/.jpeg/.png`) e MIME type real detectado via `python-magic` a partir
   dos bytes do arquivo, comparado contra a extensão informada — nunca se
   confia no `Content-Type` enviado pelo cliente. Tamanho verificado após a
   leitura, contra `MAX_UPLOAD_SIZE`.
2. Nome de arquivo sempre gerado com `uuid4().hex` + extensão validada, salvo
   em `UPLOAD_DIR/documentos/` ou `UPLOAD_DIR/fotos/`. O nome/caminho original
   do upload nunca é usado para gravação em disco.
3. `POST /api/solicitacoes` (público, sem autenticação) cria a solicitação:
   valida consentimento LGPD obrigatório, gera protocolo sequencial anual
   (`solicitacao_repository.gerar_protocolo`) com retry em caso de colisão
   (`IntegrityError` na constraint `unique` de `protocolo`), grava os arquivos
   e registra o evento "Solicitação criada" no histórico. Rate limit de
   5 requisições/minuto por IP (slowapi), conforme §12.
4. `GET /api/solicitacoes/{id}/documentos/{tipo}` (protegido, exige
   autenticação) serve o arquivo via `FileResponse`, resolvendo o caminho a
   partir do banco — nunca a partir de entrada do cliente — e validando que o
   caminho resolvido permanece dentro de `UPLOAD_DIR` antes de servir
   (defesa contra path traversal caso o dado em banco seja corrompido).

Motivo: opção mais simples e segura para o MVP que atende integralmente ao
§12 sem introduzir infraestrutura extra (ex.: object storage) nesta fase.

Arquivos afetados: `backend/app/utils/file_validation.py`,
`backend/app/services/upload_service.py`,
`backend/app/api/routes/solicitacoes.py`,
`backend/app/schemas/solicitacao.py`.

**Adendo 35.4 — Envio de e-mail: quando é permitido e tratamento de falha**

Contexto: o §26 pede a ação "Enviar resposta" via SMTP sem detalhar em quais
status ela é permitida nem o que fazer quando o envio falha.

Decisão: `POST /api/solicitacoes/{id}/enviar-email` só é permitido com status
`aprovada` ou `rejeitada` (o médico só recebe resposta depois de uma decisão).
O envio não altera o status automaticamente — "marcar como respondida"
continua sendo uma ação separada e explícita do técnico. Falha de envio (SMTP
não configurado ou erro de rede) é registrada em `Comunicacao`
(`status_envio=falha`, com a mensagem de erro) e no histórico ("Falha ao
enviar e-mail"), e a API retorna 502 — nunca falha silenciosamente. Sucesso
gera o evento "Credenciais enviadas por e-mail" no histórico, conforme os
exemplos do §9.

Motivo: mantém o fluxo auditável mesmo quando o SMTP de desenvolvimento não
está configurado (`.env` local tem `SMTP_HOST` vazio), e evita duplicar a
decisão de status entre "enviar e-mail" e "marcar respondida".

Arquivos afetados: `backend/app/core/email.py`,
`backend/app/repositories/comunicacao_repository.py`,
`backend/app/services/solicitacao_service.py`,
`backend/app/api/routes/solicitacoes.py`.

**Adendo 35.5 — Gerenciamento de usuários e scripts Windows**

Contexto: §11 (gerenciamento de usuários) e §18 (scripts Windows) não
detalham a API nem a localização dos scripts.

Decisão:
1. `/api/usuarios/*` (listar, criar, atualizar perfil/status, redefinir
   senha) exige perfil `administrador` (`require_perfil`), diferente dos
   endpoints de solicitações que aceitam qualquer perfil autenticado — aqui
   o §11 é explícito ("Administrador: gerencia usuários"). Um administrador
   não pode desativar a si mesmo (evita perda acidental de acesso quando há
   apenas um admin).
2. Scripts opcionais (§18) em `scripts/windows/` na raiz do repositório:
   `setup-backend.bat`/`setup-frontend.bat` (primeira configuração) e
   `start-backend.bat`/`start-frontend.bat`/`start-dev.bat` (inicialização
   do dia a dia). Não substituem a documentação do README (etapa 19) — são
   um atalho opcional, conforme pedido no §18.

Arquivos afetados: `backend/app/api/routes/usuarios.py`,
`backend/app/schemas/user.py`, `backend/app/repositories/user_repository.py`,
`frontend/src/pages/admin/Usuarios.tsx`, `scripts/windows/*.bat`.

**Adendo 35.6 — Framework de testes e escopo do teste de integração**

Contexto: a seção "Testes" do CLAUDE.md deixa o framework em aberto; a etapa
18 do §33 pede "testar integração frontend/backend" sem especificar o
mecanismo.

Decisão: `pytest` + `TestClient` do FastAPI (ambos já em `requirements.txt`),
em `backend/tests/test_integracao_fluxo_completo.py`. Os testes rodam contra
o próprio MySQL de desenvolvimento configurado no `.env` — não foi criado um
banco de teste isolado nesta fase do MVP — e cada teste limpa os dados que
cria ao final. Cobre o fluxo principal (§2) de ponta a ponta: criação pública
com upload, listagem/filtro, detalhe sem expor paths, visualização de
documento, transições de status até "respondida", histórico, dashboard, e
autorização (401 sem login, 403 técnico tentando gerenciar usuários). Também
validado manualmente: `npm run build` do frontend gera bundle de produção sem
erros (aviso de tamanho de chunk >500KB é aceitável para o MVP, sem
code-splitting nesta fase).

Motivo: opção mais simples que não exige infraestrutura de banco adicional;
adequado ao volume de dados de um MVP. Deve ser revisto (banco de teste
dedicado) se a suíte crescer ou rodar em CI compartilhado.

Arquivos afetados: `backend/tests/test_integracao_fluxo_completo.py`.

**Adendo 35.7 — Login por usuário (`login`), além do e-mail**

Contexto: o BLUEPRINT original (§12) previa autenticação apenas por e-mail.
O usuário pediu, após o MVP inicial, a opção de logar também por um
identificador de usuário curto.

Decisão: novo campo `login` em `users` (`String(50)`, único, padrão
`^[a-zA-Z0-9._-]{3,50}$`), definido manualmente na criação/edição do usuário
pela tela de Usuários (sem geração automática). `POST /api/auth/login` passa
a receber `login_ou_email` e busca o usuário por `email` OU `login`
(`user_repository.get_by_login_ou_email`). Usuários existentes no banco
receberam um login provisório via migration (`a3a823258a92`), gerado a partir
da parte do e-mail antes do `@` — o administrador deve revisar/ajustar esses
logins provisórios conforme necessário.

Motivo: opção mais simples pedida explicitamente pelo usuário; manter o
e-mail como identificador alternativo (em vez de substituí-lo) evita quebrar
o fluxo de login já validado e não exige alterar `Solicitacao` nem nenhuma
outra tabela.

Arquivos afetados: `backend/app/models/user.py`,
`backend/migrations/versions/a3a823258a92_*.py`,
`backend/app/schemas/auth.py`, `backend/app/schemas/user.py`,
`backend/app/repositories/user_repository.py`,
`backend/app/api/routes/auth.py`, `backend/app/api/routes/usuarios.py`,
`backend/scripts/seed_admin.py`,
`frontend/src/pages/admin/Login.tsx`, `frontend/src/pages/admin/Usuarios.tsx`,
`frontend/src/contexts/AuthContext.tsx`, `frontend/src/services/authApi.ts`,
`frontend/src/services/usuarioApi.ts`.

**Adendo 35.8 — Identidade visual INGOH (paleta, tipografia, logo)**

Contexto: o BLUEPRINT não especifica identidade visual/branding. O usuário
pediu explicitamente que o frontend (público e administrativo) refletisse a
marca da INGOH (https://ingoh.com.br/), mantendo a estrutura funcional atual
— sem alterar rotas, lógica ou chamadas de API.

Decisão: paleta e tipografia extraídas diretamente do CSS real do site (não
estimadas), a partir dos arquivos gerados pelo Elementor
(`--e-global-color-primary/secondary/text` em `post-4.css` e uso confirmado
em `post-430.css`/`post-6022.css`) e dos `@font-face` carregados
(`font-family:"Montserrat"` majoritário em headings, `"Open Sans"` no corpo):

- Primária: `#99153E` (bordô) — botões, links, destaques
- Primária escura: `#5A0C23` — header administrativo, hover de botões, estado "Rejeitada"
- Texto padrão: `#535353` / texto escuro: `#2E2E2E`
- Neutros de fundo: `#FDFDFD` (cards), `#F5F5F5` (fundo de página), `#EEEEEE`/`#E4E4E4` (bordas)
- Tipografia: `Montserrat` (headings) + `Open Sans` (corpo), via Google Fonts
- Uma cor `--accent:#00C3FF` estava definida nas variáveis globais do
  Elementor mas sem uso real detectado em nenhum elemento visível do site —
  **não foi adotada**, para não introduzir uma cor fora da identidade
  efetivamente aplicada pela INGOH.

Todas as cores foram centralizadas em variáveis CSS (`:root` em
`frontend/src/index.css`), nenhuma cor hex solta nos componentes. Badges de
status usam uma cor por status, cada uma auditada contra WCAG AA
(mínimo 4.5:1 texto/fundo):

| Status | Fundo | Texto | Contraste |
|---|---|---|---|
| Pendente | `#FCEACB` | `#7A5300` | 5.80:1 |
| Em análise | `#DCE6EA` | `#2F4858` | 7.56:1 |
| Aprovada | `#DCEFE0` | `#1E5631` | 7.19:1 |
| Rejeitada | `#F5DCE3` | `#5A0C23` | 10.74:1 |
| Respondida | `#E4E4E4` | `#2E2E2E` | 10.68:1 |

Botões primários (branco sobre `#99153E`: 8.30:1) e o header administrativo
(branco sobre `#5A0C23`: 13.89:1) também auditados e aprovados.

Logo oficial baixado do próprio site e versionado em `frontend/src/assets/`
(`ingoh-marca.webp` — versão colorida, usada no header público;
`ingoh-marca-branca.webp` — versão branca, usada no header administrativo
escuro; `ingoh-bola-192.webp` — símbolo circular, usado como favicon).

Motivo: opção mais fiel possível à marca real (dados extraídos do CSS
computado, não estimados), evitando introduzir cores fora do sistema visual
da instituição, mantida a sobriedade esperada de uma instituição de saúde
certificada (sem cores muito saturadas, sem ícones informais).

Arquivos afetados: `frontend/index.html`, `frontend/src/index.css`,
`frontend/src/layouts/PublicLayout.tsx`, `frontend/src/layouts/AdminLayout.tsx`,
`frontend/src/pages/admin/SolicitacoesLista.tsx`,
`frontend/src/pages/admin/SolicitacaoDetalhe.tsx`,
`frontend/src/assets/ingoh-marca.webp`,
`frontend/src/assets/ingoh-marca-branca.webp`,
`frontend/src/assets/ingoh-bola-192.webp`, `frontend/public/favicon.webp`.

**Adendo 35.9 — CORS multi-origem e URL de API dinâmica para testes na rede local**

Contexto: durante o desenvolvimento, o usuário precisou acessar o frontend a
partir do IP da máquina na rede local (para testar de outros dispositivos),
o que quebrava de duas formas: o Vite só escutava em `localhost`, e o
backend rejeitava a origem por CORS (`allow_origins` aceitava apenas uma
única URL), além do cliente axios ter a URL da API fixa em
`http://localhost:8000/api`.

Decisão: `FRONTEND_URL` (`.env`) passa a aceitar múltiplas origens separadas
por vírgula (`Settings.frontend_urls`, usado em `CORSMiddleware(allow_origins=...)`
em `app/main.py`). No frontend, a baseURL do axios (`services/api.ts`) deixa
de ser fixa e passa a ser derivada de `window.location.hostname` quando
`VITE_API_URL` não está definida — assim a mesma build funciona acessada por
`localhost` ou pelo IP da máquina, sem reconfiguração. Em dev, os servidores
sobem com `--host` (Vite) e `--host 0.0.0.0` (uvicorn) para escutar em todas
as interfaces. Nada disso é usado em produção: lá `FRONTEND_URL` continua
sendo uma única URL pública e `VITE_API_URL` é definida explicitamente no
build (§20-22).

Motivo: opção mais simples que atende à necessidade de teste em múltiplos
dispositivos na rede local sem comprometer a configuração de produção
(CORS de origem única) nem exigir hardcode de IP em código versionado — o
IP da rede local fica apenas no `.env` local (não versionado).

Arquivos afetados: `backend/app/core/config.py`, `backend/app/main.py`,
`backend/.env.example`, `frontend/src/services/api.ts`.

**Adendo 35.10 — Aviso de prazo de envio de credenciais na tela de sucesso**

Contexto: o usuário pediu que a tela de confirmação do formulário público
(`/solicitacao/sucesso`) informasse explicitamente o prazo e os canais de
envio de login/senha, além do número de protocolo já exibido.

Decisão: adicionado o texto "Você receberá seu login e senha por WhatsApp ou
e-mail em até 24 horas." logo abaixo do protocolo. É apenas um texto
informativo na tela — nenhum SLA de 24h nem envio automático por WhatsApp foi
implementado no backend. Hoje (§26-27) o envio de e-mail é automático via
`POST /api/solicitacoes/{id}/enviar-email`, mas o WhatsApp continua sendo o
fluxo manual do MVP ("copiar mensagem para WhatsApp", §27) — a promessa de
"WhatsApp em até 24h" depende de o técnico responsável executar essa etapa
manualmente dentro do prazo; não é garantida pelo sistema.

Motivo: mudança de texto pedida explicitamente pelo usuário. Registrada aqui
para deixar claro que a UI promete algo (prazo, canal WhatsApp automático)
que o backend ainda não garante — caso o WhatsApp automático (Meta WhatsApp
Cloud API, citado no §27 como evolução futura) ou um lembrete de SLA sejam
implementados depois, este adendo deve ser atualizado.

Arquivos afetados: `frontend/src/pages/publico/SolicitacaoSucesso.tsx`.

**Adendo 35.11 — Campo "Conselho" como lista fixa de opções**

Contexto: o §3 (formulário público) pedia o campo "Conselho" como texto livre
(placeholder "ex: CRM"). O usuário pediu que virasse uma caixa de seleção com
uma lista fixa de conselhos profissionais, CRM sempre como primeira opção.

Decisão: campo `conselho` do formulário público passa a ser um `<select>`
com as opções, nesta ordem: CRM, CRO, CRN, CRBM, CFF, COREN, CREFITO,
CREFONO, CRBio, e por último "Outros (especifique)". Ao selecionar "Outros",
um campo de texto adicional (`conselho_outro`, não persistido — existe só no
formulário) é exibido e se torna obrigatório (mínimo 2 caracteres); no
envio, o valor final gravado no campo `conselho` da API é o texto digitado
em "Outros", não a string `"outros"`. Nenhuma mudança no backend/banco: a
coluna `conselho` continua `String` livre (§14), a lista de opções é
validação/UX apenas do frontend (`zod` + `react-hook-form`).

Motivo: opção mais simples pedida explicitamente pelo usuário, que evita
alterar o schema do banco ou da API — mantém `conselho` como texto livre no
backend (compatível com conselhos não previstos na lista) enquanto restringe
as opções mais comuns na interface para reduzir erro de digitação.

Arquivos afetados: `frontend/src/pages/publico/SolicitacaoForm.tsx`.

**Adendo 35.12 — Configuração de SMTP pela área administrativa (exceção à regra "secrets sempre via .env")**

Contexto: o §25/CLAUDE.md estabelece que secrets — explicitamente citando
SMTP — devem ficar sempre em variável de ambiente, nunca no banco. Ao
investigar uma falha de envio de e-mail (SMTP não configurado no `.env` de
dev), o usuário pediu explicitamente que a configuração de SMTP passasse a
ser feita pela própria aplicação web (tela administrativa), em vez de exigir
acesso ao `.env` do servidor. Diante do conflito com a regra fixa do
CLAUDE.md, a exceção foi confirmada explicitamente pelo usuário antes da
implementação.

Decisão:
1. Nova tabela `smtp_config` (linha única, id fixo `1`): `host`, `port`,
   `usuario`, `senha_criptografada`, `remetente`, `updated_at`, `updated_by`.
   A senha nunca é gravada em texto puro — é criptografada simetricamente
   (`cryptography.fernet.Fernet`) com chave derivada de `SECRET_KEY`
   (`app/core/crypto.py`), então nenhum novo secret precisa ser adicionado ao
   `.env`. A senha também nunca é devolvida pela API (`SmtpConfigOut` expõe
   apenas `senha_configurada: bool`).
2. `GET/PUT /api/configuracoes/smtp` e `POST /api/configuracoes/smtp/testar`
   (envia e-mail de teste real) exigem perfil `administrador`
   (`require_perfil`, mesmo padrão de `/api/usuarios`). Tela "Configurações"
   no menu administrativo (visível só para administrador, mesmo padrão de
   "Usuários"), com formulário de host/porta/usuário/senha/remetente e um
   formulário separado de teste de envio.
3. `app/core/email.py` deixou de ler `Settings` (`.env`) e passou a carregar
   a configuração de `smtp_config` via `db: Session` (novo parâmetro
   obrigatório de `enviar_email`); os campos `smtp_*` foram removidos de
   `Settings`/`.env.example`/`.env`. `EmailNaoConfiguradoError` agora dispara
   quando não há linha em `smtp_config` (nenhuma migration de dados — quem
   tinha SMTP configurado via `.env` precisa recadastrar pela tela).
4. Testado via Playwright contra o app rodando (login como admin, salvar
   configuração, reload confirma persistência e placeholder "manter senha
   atual", teste de envio contra host inválido retorna erro 502 legível na
   tela) e verificação direta no MySQL de que `senha_criptografada` não é a
   senha em texto puro.

Motivo: atende ao pedido explícito do usuário de eliminar a dependência de
acesso ao arquivo `.env` do servidor para configurar e-mail — útil sobretudo
em produção (Linux), onde só quem tem acesso SSH/systemd poderia editar o
`.env` hoje. A criptografia em repouso com chave derivada do `SECRET_KEY`
(já um secret protegido por env var) foi o compromisso mais simples que
preserva a intenção de segurança da regra original (nunca texto puro,
nunca exposto pela API) sem reintroduzir a dependência de arquivo.

Arquivos afetados: `backend/app/core/crypto.py`, `backend/app/core/email.py`,
`backend/app/core/config.py`, `backend/app/models/smtp_config.py`,
`backend/app/models/__init__.py`,
`backend/app/repositories/smtp_config_repository.py`,
`backend/app/schemas/smtp_config.py`,
`backend/app/api/routes/configuracoes.py`,
`backend/app/api/routes/__init__.py`,
`backend/app/services/solicitacao_service.py`,
`backend/migrations/versions/75c487ef0680_cria_tabela_smtp_config.py`,
`backend/.env.example`,
`frontend/src/services/configuracaoApi.ts`,
`frontend/src/pages/admin/Configuracoes.tsx`,
`frontend/src/routes/AppRoutes.tsx`, `frontend/src/layouts/AdminLayout.tsx`,
`frontend/src/index.css`.

**Adendo 35.13 — Anexo opcional no e-mail de resposta ao médico**

Contexto: o usuário pediu para anexar um arquivo (PDF, JPG ou PNG) à
mensagem enviada em `POST /api/solicitacoes/{id}/enviar-email` (§26), que
antes só aceitava texto.

Decisão: o endpoint passou de JSON (`{"mensagem": ...}`) para
`multipart/form-data` (`mensagem` como campo de formulário, `anexo` como
arquivo opcional), reaproveitando integralmente a mesma validação dos
uploads do formulário público (`validar_e_ler_upload` — allowlist de
extensão `.pdf/.jpg/.jpeg/.png`, MIME real via `python-magic`, limite de
`MAX_UPLOAD_SIZE`). O anexo nunca é salvo em disco nem em `UPLOAD_DIR`: fica
em memória durante a requisição, é anexado à mensagem SMTP
(`EmailMessage.add_attachment`) com nome fixo `anexo<extensão>` (nunca o
nome original do arquivo, para não expor metadados nem permitir injeção via
nome de arquivo) e descartado ao final do envio. O evento "Credenciais
enviadas por e-mail" no histórico (§9) passa a registrar "Enviado com
anexo" quando aplicável, para manter a auditoria.

Motivo: opção mais simples que atende ao pedido sem introduzir uma segunda
categoria de arquivo armazenado — como o anexo é conteúdo transitório
(enviado e descartado, nunca consultado depois pela aplicação), não há
motivo para persisti-lo em `UPLOAD_DIR` nem gerar um path auditável como os
documentos da solicitação original.

Testado via Playwright contra o app rodando: solicitação de teste criada
via API, aprovada, anexo PNG enviado pela tela para um e-mail de teste
(`@example.com`, domínio reservado que nunca entrega a pessoa real),
histórico confirmando "Enviado com anexo". Dados de teste removidos após a
verificação.

Arquivos afetados: `backend/app/core/email.py`,
`backend/app/services/solicitacao_service.py`,
`backend/app/api/routes/solicitacoes.py`, `backend/app/schemas/solicitacao.py`,
`backend/tests/test_integracao_fluxo_completo.py`,
`frontend/src/services/solicitacaoAdminApi.ts`,
`frontend/src/pages/admin/SolicitacaoDetalhe.tsx`.

**Adendo 35.14 — Assunto e cabeçalho fixos identificando a INGOH no e-mail de resposta**

Contexto: o assunto e o corpo do e-mail enviado em "Enviar resposta por
e-mail" (§26) eram genéricos — assunto fixo "Solicitação de acesso -
resultado da análise" e corpo 100% livre, digitado pelo técnico (ex.:
"usuario X / senha X"), sem identificar a INGOH nem repetir o
resultado/protocolo. O usuário pediu que ficasse mais claro que é o
resultado da análise da INGOH.

Decisão: `solicitacao_service.enviar_email_resposta` passou a montar
assunto e um cabeçalho fixos a partir dos dados da própria solicitação,
antes do texto livre do técnico:
- Assunto: `INGOH - Resultado da análise da sua solicitação de acesso
  ({protocolo})`.
- Corpo: saudação com `nome_completo`, uma linha fixa citando "INGOH",
  o protocolo e o resultado (`APROVADA`/`REJEITADA`, derivado do
  `status` atual da solicitação), seguida em branco pelo texto que o
  técnico digitou na tela (mensagem/credenciais), sem alterar esse campo.

Motivo: opção mais simples que resolve a ambiguidade sem tirar do técnico o
controle sobre o conteúdo específico da mensagem (credenciais, orientações)
— o cabeçalho fixo garante que todo e-mail enviado pelo sistema já
identifica a INGOH e o resultado, independentemente do que o técnico
escrever.

Arquivos afetados: `backend/app/services/solicitacao_service.py`.

**Adendo 35.15 — README/DEPLOY_LINUX.md atualizados para publicação no GitHub**

Contexto: ao preparar o repositório para publicação no GitHub, o usuário
pediu para revisar o `README.md` e expandir `docs/DEPLOY_LINUX.md` em um
guia completo do zero (§19-25 do BLUEPRINT).

Decisão / correções:
1. **Bug fora do escopo original, corrigido**: os comandos de exemplo do
   `scripts.seed_admin` no `README.md` e no `DEPLOY_LINUX.md` estavam sem o
   argumento `--login`, que se tornou obrigatório no Adendo 35.7 (login por
   usuário) — o comando documentado falharia com `error: the following
   arguments are required: --login`. Corrigido nos dois arquivos.
2. `DEPLOY_LINUX.md` reescrito com: instalação completa de dependências de
   SO (incluindo `certbot`/`python3-certbot-apache`, que só era mencionado
   no exemplo de VirtualHost, não na lista de pacotes); Node.js via
   repositório oficial NodeSource (`deb.nodesource.com/setup_lts.x`) — o
   pacote `nodejs` dos repositórios padrão do Ubuntu/Debian costuma estar
   desatualizado para o Vite; `.env` de produção completo e sincronizado
   com `backend/.env.example` atual (`ACCESS_TOKEN_EXPIRE_MINUTES`, que
   faltava, e sem `SMTP_*`, removido do `.env` desde o Adendo 35.12, com
   nota explícita direcionando à tela "Configurações"); fluxo HTTP-primeiro
   → Certbot (VirtualHost `:80` sem SSL, `a2ensite`, reload, só depois
   `certbot --apache`) em vez de um VirtualHost `:443` de exemplo estático,
   com a alternativa manual (`certbot certonly --apache`) para quem já tem
   VirtualHost customizado; verificação de renovação automática
   (`certbot renew --dry-run`, `systemctl status certbot.timer`).
3. Checklist pós-deploy (§8) ganhou itens para testar visualização
   autenticada de documento/foto e o teste de envio de SMTP pela tela
   "Configurações".

Motivo: o guia anterior presumia conhecimento prévio do projeto (ex.: não
instalava Node.js, não listava `certbot` como pacote, referenciava
variáveis de SMTP que não existem mais) — inadequado para alguém instalar o
MVP do zero, que era o objetivo explícito do pedido.

Arquivos afetados: `README.md`, `docs/DEPLOY_LINUX.md`.
