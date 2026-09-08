from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import StatusSolicitacao


class SolicitacaoListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    protocolo: str
    nome_completo: str
    conselho: str
    numero_conselho: str
    uf_conselho: str
    especialidade: str
    email: str
    telefone: str
    status: StatusSolicitacao
    responsavel_nome: str | None = None
    created_at: datetime


class SolicitacaoListResponse(BaseModel):
    items: list[SolicitacaoListItem]
    total: int
    page: int
    page_size: int


class SolicitacaoDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    protocolo: str
    nome_completo: str
    conselho: str
    numero_conselho: str
    uf_conselho: str
    especialidade: str
    email: str
    telefone: str
    status: StatusSolicitacao
    observacao_interna: str | None
    motivo_rejeicao: str | None
    responsavel_nome: str | None = None
    created_at: datetime
    updated_at: datetime
    analise_iniciada_at: datetime | None
    analisado_at: datetime | None
    respondido_at: datetime | None


class RejeitarRequest(BaseModel):
    motivo: str = Field(min_length=3, max_length=2000)


class ObservacaoRequest(BaseModel):
    observacao_interna: str = Field(max_length=2000)


class SolicitacaoFiltros(BaseModel):
    status: StatusSolicitacao | None = None
    nome: str | None = None
    numero_conselho: str | None = None
    conselho: str | None = None
    especialidade: str | None = None
    data_inicial: date | None = None
    data_final: date | None = None
    busca: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
