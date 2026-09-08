from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import StatusSolicitacao
from app.models.solicitacao import Solicitacao
from app.schemas.dashboard import DashboardCards, PontoSerieDiaria


def obter_cards(db: Session) -> DashboardCards:
    hoje_inicio = datetime.combine(date.today(), time.min)
    hoje_fim = datetime.combine(date.today(), time.max)

    contagem_status = dict(
        db.execute(
            select(Solicitacao.status, func.count()).group_by(Solicitacao.status)
        ).all()
    )

    total = sum(contagem_status.values())
    recebidas_hoje = db.execute(
        select(func.count()).where(Solicitacao.created_at.between(hoje_inicio, hoje_fim))
    ).scalar_one()

    return DashboardCards(
        total=total,
        recebidas_hoje=recebidas_hoje,
        pendentes=contagem_status.get(StatusSolicitacao.PENDENTE, 0),
        em_analise=contagem_status.get(StatusSolicitacao.EM_ANALISE, 0),
        aprovadas=contagem_status.get(StatusSolicitacao.APROVADA, 0),
        rejeitadas=contagem_status.get(StatusSolicitacao.REJEITADA, 0),
        respondidas=contagem_status.get(StatusSolicitacao.RESPONDIDA, 0),
    )


def obter_serie_30_dias(db: Session) -> list[PontoSerieDiaria]:
    inicio = datetime.combine(date.today() - timedelta(days=29), time.min)
    data_coluna = func.date(Solicitacao.created_at)

    linhas = dict(
        db.execute(
            select(data_coluna, func.count())
            .where(Solicitacao.created_at >= inicio)
            .group_by(data_coluna)
        ).all()
    )

    serie = []
    for i in range(30):
        dia = date.today() - timedelta(days=29 - i)
        total = linhas.get(dia, 0)
        serie.append(PontoSerieDiaria(data=dia, total=total))
    return serie


def obter_distribuicao_status(db: Session) -> dict[str, int]:
    linhas = db.execute(select(Solicitacao.status, func.count()).group_by(Solicitacao.status)).all()
    return {status.value: total for status, total in linhas}
