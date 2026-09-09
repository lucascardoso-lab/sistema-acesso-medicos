from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import PerfilUsuario


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    login: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[PerfilUsuario] = mapped_column(
        Enum(PerfilUsuario, native_enum=False, length=20), nullable=False
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    solicitacoes_responsavel = relationship(
        "Solicitacao", back_populates="responsavel", foreign_keys="Solicitacao.responsavel_id"
    )
    historico_eventos = relationship("HistoricoSolicitacao", back_populates="usuario")
