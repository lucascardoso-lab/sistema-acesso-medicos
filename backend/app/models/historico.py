from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class HistoricoSolicitacao(Base):
    __tablename__ = "historico_solicitacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    solicitacao_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("solicitacoes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    usuario_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    acao: Mapped[str] = mapped_column(String(100), nullable=False)
    status_anterior: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status_novo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    solicitacao = relationship("Solicitacao", back_populates="historico")
    usuario = relationship("User", back_populates="historico_eventos")
