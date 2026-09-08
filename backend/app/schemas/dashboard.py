from datetime import date

from pydantic import BaseModel


class DashboardCards(BaseModel):
    total: int
    recebidas_hoje: int
    pendentes: int
    em_analise: int
    aprovadas: int
    rejeitadas: int
    respondidas: int


class PontoSerieDiaria(BaseModel):
    data: date
    total: int


class DashboardResponse(BaseModel):
    cards: DashboardCards
    serie_30_dias: list[PontoSerieDiaria]
    distribuicao_status: dict[str, int]
