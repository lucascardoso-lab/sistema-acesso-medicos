import smtplib
from email.message import EmailMessage

from app.core.config import get_settings

settings = get_settings()


class EmailNaoConfiguradoError(Exception):
    pass


def enviar_email(destinatario: str, assunto: str, corpo: str) -> None:
    if not settings.smtp_host or not settings.smtp_from:
        raise EmailNaoConfiguradoError("SMTP não configurado (SMTP_HOST/SMTP_FROM ausentes)")

    mensagem = EmailMessage()
    mensagem["Subject"] = assunto
    mensagem["From"] = settings.smtp_from
    mensagem["To"] = destinatario
    mensagem.set_content(corpo)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as servidor:
        servidor.starttls()
        if settings.smtp_user and settings.smtp_password:
            servidor.login(settings.smtp_user, settings.smtp_password)
        servidor.send_message(mensagem)
