from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.historico import HistoricoSolicitacao
from app.models.user import User


def registrar(
    db: Session,
    *,
    solicitacao_id: int,
    usuario: User | None,
    acao: str,
    status_anterior: str | None = None,
    status_novo: str | None = None,
    descricao: str | None = None,
) -> HistoricoSolicitacao:
    evento = HistoricoSolicitacao(
        solicitacao_id=solicitacao_id,
        usuario_id=usuario.id if usuario else None,
        acao=acao,
        status_anterior=status_anterior,
        status_novo=status_novo,
        descricao=descricao,
    )
    db.add(evento)
    db.flush()
    return evento


def listar_por_solicitacao(db: Session, solicitacao_id: int) -> list[HistoricoSolicitacao]:
    stmt = (
        select(HistoricoSolicitacao)
        .options(joinedload(HistoricoSolicitacao.usuario))
        .where(HistoricoSolicitacao.solicitacao_id == solicitacao_id)
        .order_by(HistoricoSolicitacao.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())
