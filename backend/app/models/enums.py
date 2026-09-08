import enum


class PerfilUsuario(str, enum.Enum):
    ADMINISTRADOR = "administrador"
    TECNICO = "tecnico"


class StatusSolicitacao(str, enum.Enum):
    PENDENTE = "pendente"
    EM_ANALISE = "em_analise"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    RESPONDIDA = "respondida"


class CanalComunicacao(str, enum.Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"


class StatusEnvio(str, enum.Enum):
    SUCESSO = "sucesso"
    FALHA = "falha"
