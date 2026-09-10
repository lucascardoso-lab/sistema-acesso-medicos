import smtplib
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.core.crypto import descriptografar
from app.repositories import smtp_config_repository


class EmailNaoConfiguradoError(Exception):
    pass


MIME_POR_EXTENSAO = {
    ".pdf": ("application", "pdf"),
    ".jpg": ("image", "jpeg"),
    ".jpeg": ("image", "jpeg"),
    ".png": ("image", "png"),
}


def enviar_email(
    db: Session,
    destinatario: str,
    assunto: str,
    corpo: str,
    anexo: tuple[bytes, str] | None = None,
) -> None:
    config = smtp_config_repository.obter(db)
    if not config or not config.host or not config.remetente:
        raise EmailNaoConfiguradoError(
            "SMTP não configurado — acesse Configurações na área administrativa"
        )

    mensagem = EmailMessage()
    mensagem["Subject"] = assunto
    mensagem["From"] = config.remetente
    mensagem["To"] = destinatario
    mensagem.set_content(corpo)

    if anexo:
        conteudo, extensao = anexo
        maintype, subtype = MIME_POR_EXTENSAO[extensao]
        mensagem.add_attachment(
            conteudo, maintype=maintype, subtype=subtype, filename=f"anexo{extensao}"
        )

    with smtplib.SMTP(config.host, config.port, timeout=10) as servidor:
        servidor.starttls()
        if config.usuario and config.senha_criptografada:
            servidor.login(config.usuario, descriptografar(config.senha_criptografada))
        servidor.send_message(mensagem)
