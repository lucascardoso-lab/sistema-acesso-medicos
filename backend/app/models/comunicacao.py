from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import CanalComunicacao, StatusEnvio


class Comunicacao(Base):
    __tablename__ = "comunicacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    solicitacao_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("solicitacoes.id", ondelete="CASCADE"), nullable=False, index=True
    )

    canal: Mapped[CanalComunicacao] = mapped_column(
        Enum(CanalComunicacao, native_enum=False, length=20), nullable=False
    )
    destinatario: Mapped[str] = mapped_column(String(150), nullable=False)
    status_envio: Mapped[StatusEnvio] = mapped_column(
        Enum(StatusEnvio, native_enum=False, length=20), nullable=False
    )
    enviado_por: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    enviado_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    erro: Mapped[str | None] = mapped_column(Text, nullable=True)

    solicitacao = relationship("Solicitacao", back_populates="comunicacoes")
