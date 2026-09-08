from sqlalchemy.orm import Session

from app.models.comunicacao import Comunicacao
from app.models.enums import CanalComunicacao, StatusEnvio
from app.models.user import User


def registrar(
    db: Session,
    *,
    solicitacao_id: int,
    destinatario: str,
    status_envio: StatusEnvio,
    enviado_por: User | None,
    erro: str | None = None,
) -> Comunicacao:
    comunicacao = Comunicacao(
        solicitacao_id=solicitacao_id,
        canal=CanalComunicacao.EMAIL,
        destinatario=destinatario,
        status_envio=status_envio,
        enviado_por=enviado_por.id if enviado_por else None,
        erro=erro,
    )
    db.add(comunicacao)
    db.flush()
    return comunicacao
