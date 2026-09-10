from sqlalchemy.orm import Session

from app.core.crypto import criptografar
from app.models.smtp_config import SmtpConfig
from app.models.user import User

CONFIG_ID = 1


def obter(db: Session) -> SmtpConfig | None:
    return db.get(SmtpConfig, CONFIG_ID)


def salvar(
    db: Session,
    *,
    host: str,
    port: int,
    usuario: str,
    remetente: str,
    senha: str | None,
    atualizado_por: User,
) -> SmtpConfig:
    senha_normalizada = "".join(senha.split()) if senha else None

    config = obter(db)
    if config is None:
        config = SmtpConfig(
            id=CONFIG_ID,
            host=host,
            port=port,
            usuario=usuario,
            remetente=remetente,
            updated_by=atualizado_por.id,
        )
        if senha_normalizada:
            config.senha_criptografada = criptografar(senha_normalizada)
        db.add(config)
    else:
        config.host = host
        config.port = port
        config.usuario = usuario
        config.remetente = remetente
        if senha_normalizada:
            config.senha_criptografada = criptografar(senha_normalizada)
        config.updated_by = atualizado_por.id

    db.commit()
    db.refresh(config)
    return config
