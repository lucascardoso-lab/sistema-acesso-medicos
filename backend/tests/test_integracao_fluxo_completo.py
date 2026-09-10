"""Teste de integração ponta a ponta do fluxo principal (BLUEPRINT secao 2).

Roda contra o banco MySQL de desenvolvimento configurado em .env (nao ha banco
de teste isolado nesta fase do MVP - decisao registrada no Adendo 35.6). Cada
teste limpa os proprios dados ao final.
"""

from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.main import app
from app.models.solicitacao import Solicitacao
from app.models.user import User

PDF_VALIDO = b"%PDF-1.4\n%%EOF"
JPG_VALIDO = bytes.fromhex("ffd8ffe000104a46494600010100000100010000") + b"\x00" * 50 + bytes.fromhex("ffd9")

ADMIN_EMAIL = "admin@teste.com"
ADMIN_SENHA = "SenhaForte123!"


def _criar_solicitacao(client: TestClient, email: str) -> str:
    data = {
        "nome_completo": "Dra Integracao Teste",
        "conselho": "CRM",
        "numero_conselho": "555444",
        "uf_conselho": "SP",
        "especialidade": "Ortopedia",
        "email": email,
        "telefone": "11977776666",
        "consentimento_lgpd": "true",
    }
    files = {
        "documento": ("doc.pdf", PDF_VALIDO, "application/pdf"),
        "foto_documento": ("foto.jpg", JPG_VALIDO, "image/jpeg"),
    }
    resposta = client.post("/api/solicitacoes", data=data, files=files)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()["protocolo"]


def test_fluxo_completo_solicitacao_ate_respondida():
    client = TestClient(app)
    email_teste = "integracao@teste.com"

    try:
        protocolo = _criar_solicitacao(client, email_teste)
        assert protocolo.startswith("SOL-")

        login = client.post("/api/auth/login", json={"login_ou_email": ADMIN_EMAIL, "senha": ADMIN_SENHA})
        assert login.status_code == 200

        listagem = client.get("/api/solicitacoes", params={"busca": email_teste})
        assert listagem.status_code == 200
        itens = listagem.json()["items"]
        assert len(itens) == 1
        solicitacao_id = itens[0]["id"]
        assert itens[0]["status"] == "pendente"

        detalhe = client.get(f"/api/solicitacoes/{solicitacao_id}")
        assert detalhe.status_code == 200
        assert "documento_path" not in detalhe.json()

        doc = client.get(f"/api/solicitacoes/{solicitacao_id}/documentos/documento")
        assert doc.status_code == 200
        assert doc.headers["content-type"] == "application/pdf"

        assert client.post(f"/api/solicitacoes/{solicitacao_id}/iniciar-analise").status_code == 200
        assert client.post(f"/api/solicitacoes/{solicitacao_id}/aprovar").status_code == 200

        resposta_email = client.post(
            f"/api/solicitacoes/{solicitacao_id}/enviar-email", data={"mensagem": "teste"}
        )
        assert resposta_email.status_code in (200, 502)

        marcar = client.post(f"/api/solicitacoes/{solicitacao_id}/marcar-respondida")
        assert marcar.status_code == 200
        assert marcar.json()["status"] == "respondida"

        historico = client.get(f"/api/solicitacoes/{solicitacao_id}/historico")
        acoes = [h["acao"] for h in historico.json()]
        assert "Solicitação criada" in acoes
        assert "Solicitação marcada como respondida" in acoes

        dashboard = client.get("/api/dashboard")
        assert dashboard.status_code == 200
        assert dashboard.json()["cards"]["total"] >= 1
    finally:
        db = SessionLocal()
        db.query(Solicitacao).filter(Solicitacao.email == email_teste).delete()
        db.commit()
        db.close()


def test_usuario_nao_autenticado_nao_acessa_admin():
    client = TestClient(app)
    assert client.get("/api/solicitacoes").status_code == 401
    assert client.get("/api/dashboard").status_code == 401
    assert client.get("/api/usuarios").status_code == 401


def test_tecnico_nao_acessa_gerenciamento_de_usuarios():
    client = TestClient(app)
    email_tecnico = "tecnico.integracao@teste.com"

    client.post("/api/auth/login", json={"login_ou_email": ADMIN_EMAIL, "senha": ADMIN_SENHA})
    criado = client.post(
        "/api/usuarios",
        json={
            "nome": "Tecnico Integracao",
            "login": "tecnico.integracao",
            "email": email_tecnico,
            "senha": "SenhaForte123!",
            "perfil": "tecnico",
        },
    )
    assert criado.status_code == 201
    client.post("/api/auth/logout")

    try:
        login_tecnico = client.post(
            "/api/auth/login", json={"login_ou_email": email_tecnico, "senha": "SenhaForte123!"}
        )
        assert login_tecnico.status_code == 200

        assert client.get("/api/usuarios").status_code == 403
        assert client.get("/api/solicitacoes").status_code == 200
    finally:
        db = SessionLocal()
        db.query(User).filter(User.email == email_tecnico).delete()
        db.commit()
        db.close()
