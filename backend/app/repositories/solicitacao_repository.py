from datetime import date, datetime, time

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.solicitacao import Solicitacao
from app.schemas.solicitacao import SolicitacaoFiltros


def _aplicar_filtros(stmt: Select, filtros: SolicitacaoFiltros) -> Select:
    if filtros.status:
        stmt = stmt.where(Solicitacao.status == filtros.status)
    if filtros.nome:
        stmt = stmt.where(Solicitacao.nome_completo.ilike(f"%{filtros.nome}%"))
    if filtros.numero_conselho:
        stmt = stmt.where(Solicitacao.numero_conselho.ilike(f"%{filtros.numero_conselho}%"))
    if filtros.conselho:
        stmt = stmt.where(Solicitacao.conselho.ilike(f"%{filtros.conselho}%"))
    if filtros.especialidade:
        stmt = stmt.where(Solicitacao.especialidade.ilike(f"%{filtros.especialidade}%"))
    if filtros.data_inicial:
        stmt = stmt.where(Solicitacao.created_at >= datetime.combine(filtros.data_inicial, time.min))
    if filtros.data_final:
        stmt = stmt.where(Solicitacao.created_at <= datetime.combine(filtros.data_final, time.max))
    if filtros.busca:
        termo = f"%{filtros.busca}%"
        stmt = stmt.where(
            or_(
                Solicitacao.nome_completo.ilike(termo),
                Solicitacao.email.ilike(termo),
                Solicitacao.protocolo.ilike(termo),
                Solicitacao.numero_conselho.ilike(termo),
            )
        )
    return stmt


def listar(db: Session, filtros: SolicitacaoFiltros) -> tuple[list[Solicitacao], int]:
    base_stmt = _aplicar_filtros(select(Solicitacao), filtros)

    total = db.execute(select(func.count()).select_from(base_stmt.subquery())).scalar_one()

    stmt = (
        base_stmt.options(joinedload(Solicitacao.responsavel))
        .order_by(Solicitacao.created_at.desc())
        .offset((filtros.page - 1) * filtros.page_size)
        .limit(filtros.page_size)
    )
    itens = list(db.execute(stmt).scalars().all())
    return itens, total


def get_by_id(db: Session, solicitacao_id: int) -> Solicitacao | None:
    stmt = (
        select(Solicitacao)
        .options(joinedload(Solicitacao.responsavel))
        .where(Solicitacao.id == solicitacao_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def gerar_protocolo(db: Session) -> str:
    ano = date.today().year
    total_ano = db.execute(
        select(func.count()).where(Solicitacao.protocolo.like(f"SOL-{ano}-%"))
    ).scalar_one()
    sequencial = total_ano + 1
    return f"SOL-{ano}-{sequencial:06d}"
