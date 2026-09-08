# CLAUDE.md — Instruções do projeto para o Claude Code

Este arquivo é carregado automaticamente pelo Claude Code em toda sessão neste
projeto. Ele contém regras fixas que **não devem ser reinterpretadas ou
flexibilizadas** sem confirmação explícita do usuário.

## Sobre o projeto

Sistema web para cadastro, validação e liberação de acesso de médicos (formulário
público + área administrativa). A especificação funcional e técnica completa está
em `docs/BLUEPRINT.md` — leia esse arquivo antes de propor ou implementar
qualquer coisa. Toda decisão técnica não coberta explicitamente no BLUEPRINT deve
ser registrada como um novo adendo na seção 35 dele, não apenas decidida em
silêncio.

## Stack obrigatória (não trocar sem aprovação)

- Frontend: React + Vite + TypeScript
- Backend: Python + FastAPI + SQLAlchemy + Pydantic + Alembic
- Banco de dados: MySQL (nunca SQLite, nem "para testar rápido")
- Sem Docker, em nenhuma etapa (dev ou produção)

## Ambientes

- **Desenvolvimento:** Windows, execução local, sem Docker. Backend via
  `uvicorn --reload`, frontend via `npm run dev`, MySQL local.
- **Produção:** Linux, Apache2 como reverse proxy, backend como serviço systemd
  (Uvicorn/Gunicorn), frontend compilado (`npm run build`) servido como
  estático.
- Todo código deve funcionar nos dois ambientes: usar `pathlib`, nunca caminhos
  hardcoded, configuração sempre via variáveis de ambiente (`.env`).

## Fluxo de trabalho com git — regra bloqueante

- **Antes de qualquer `git commit` ou `git push`, mostre o diff e pare.**
  Aguarde aprovação explícita do usuário ("aprovado", "pode seguir", "comita")
  antes de prosseguir. Isso vale mesmo com alta confiança na mudança ou testes
  passando 100%.
- Nunca aprove um commit a partir de um resumo em texto — o usuário quer ver o
  diff real.
- Se durante uma correção você encontrar um bug que não fazia parte do pedido
  original, relate-o com o mesmo destaque do bug principal e registre-o também
  no adendo do BLUEPRINT.md.

## Desenvolvimento incremental

Siga a ordem definida na seção 33 do BLUEPRINT.md. Antes de cada etapa
importante, explique brevemente o que será feito e só depois implemente. Não
pare na estrutura inicial do projeto — o objetivo é chegar a um MVP funcional.

Na primeira sessão, antes de gerar qualquer código:
1. Leia `docs/BLUEPRINT.md` por completo.
2. Proponha a arquitetura e a estrutura de diretórios.
3. Aguarde aprovação explícita antes de começar a implementar.

## Segurança e privacidade — não negociável

- Documentos enviados (identificação, foto) nunca ficam em pasta pública
  (`/public`, `frontend/dist`, etc.) nem acessíveis por URL direta do Apache.
  Acesso somente via API, após autenticação.
- Nome de arquivo enviado é sempre gerado aleatoriamente — nunca confiar no
  nome original nem permitir execução do arquivo enviado.
- Senhas administrativas sempre com hash seguro; nunca texto puro, nunca em
  logs.
- Não registrar dados sensíveis (documentos, senhas, tokens) em logs.
- Secrets e credenciais (SMTP, `SECRET_KEY`, `DATABASE_URL`) sempre via
  variável de ambiente, nunca hardcoded ou versionados.
- Rate limiting no formulário público; validação de tamanho, extensão e MIME
  type no backend para todo upload.

## Regras gerais de implementação

- API sempre com prefixo `/api`; usar a documentação automática do FastAPI.
- Migrations via Alembic para toda mudança de schema — nunca alterar o banco
  manualmente "para agilizar".
- Validações no frontend **e** no backend (nunca confiar só no frontend).
- Código simples e organizado; evitar overengineering — priorizar um MVP
  funcional que possa crescer depois.
- Ao tomar qualquer decisão técnica não especificada no BLUEPRINT, escolher a
  opção mais simples, segura e fácil de manter, e documentar a decisão como
  adendo no BLUEPRINT.md (seção 35).

## Testes

- Sem framework definido ainda — se criar testes, manter simples e alinhado ao
  que for decidido no início do projeto; documentar a escolha como adendo.

## .gitignore (garantir que sempre cubra)

`.env`, `venv/`, `__pycache__/`, `node_modules/`, `frontend/dist/`, `uploads/`,
`*.log`, arquivos temporários. Nunca versionar documentos enviados, senhas,
secrets ou `.env` reais.
