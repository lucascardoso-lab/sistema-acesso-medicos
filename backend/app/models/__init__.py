from app.models.user import User
from app.models.solicitacao import Solicitacao
from app.models.historico import HistoricoSolicitacao
from app.models.comunicacao import Comunicacao
from app.models.smtp_config import SmtpConfig

__all__ = ["User", "Solicitacao", "HistoricoSolicitacao", "Comunicacao", "SmtpConfig"]
