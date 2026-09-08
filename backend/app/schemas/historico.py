from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HistoricoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    acao: str
    status_anterior: str | None
    status_novo: str | None
    descricao: str | None
    usuario_nome: str | None = None
    created_at: datetime
