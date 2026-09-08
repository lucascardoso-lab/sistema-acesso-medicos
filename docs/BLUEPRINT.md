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

(Nenhum adendo registrado ainda.)
