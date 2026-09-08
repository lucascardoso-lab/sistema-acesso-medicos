from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import StatusSolicitacao


class Solicitacao(Base):
    __tablename__ = "solicitacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    protocolo: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)

    nome_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    conselho: Mapped[str] = mapped_column(String(20), nullable=False)
    numero_conselho: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    uf_conselho: Mapped[str] = mapped_column(String(2), nullable=False)
    especialidade: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)

    documento_path: Mapped[str] = mapped_column(String(255), nullable=False)
    selfie_documento_path: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[StatusSolicitacao] = mapped_column(
        Enum(StatusSolicitacao, native_enum=False, length=20),
        nullable=False,
        default=StatusSolicitacao.PENDENTE,
        index=True,
    )
    observacao_interna: Mapped[str | None] = mapped_column(Text, nullable=True)
    motivo_rejeicao: Mapped[str | None] = mapped_column(Text, nullable=True)

    responsavel_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    consentimento_lgpd: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consentimento_versao: Mapped[str] = mapped_column(String(20), nullable=False)
    consentimento_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    analise_iniciada_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    analisado_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    respondido_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    responsavel = relationship("User", back_populates="solicitacoes_responsavel", foreign_keys=[responsavel_id])
    historico = relationship(
        "HistoricoSolicitacao", back_populates="solicitacao", cascade="all, delete-orphan"
    )
    comunicacoes = relationship(
        "Comunicacao", back_populates="solicitacao", cascade="all, delete-orphan"
    )
