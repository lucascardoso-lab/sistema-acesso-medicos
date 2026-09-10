from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_perfil
from app.core.email import EmailNaoConfiguradoError, enviar_email
from app.database.session import get_db
from app.models.enums import PerfilUsuario
from app.models.user import User
from app.repositories import smtp_config_repository
from app.schemas.smtp_config import SmtpConfigOut, SmtpConfigTestarRequest, SmtpConfigUpdateRequest

router = APIRouter(prefix="/configuracoes", tags=["configuracoes"])

exigir_admin = require_perfil(PerfilUsuario.ADMINISTRADOR)


def _to_out(config) -> SmtpConfigOut:
    return SmtpConfigOut(
        host=config.host,
        port=config.port,
        usuario=config.usuario,
        remetente=config.remetente,
        senha_configurada=bool(config.senha_criptografada),
        updated_at=config.updated_at,
    )


@router.get("/smtp", response_model=SmtpConfigOut | None)
def obter_configuracao_smtp(db: Session = Depends(get_db), _admin: User = Depends(exigir_admin)):
    config = smtp_config_repository.obter(db)
    return _to_out(config) if config else None


@router.put("/smtp", response_model=SmtpConfigOut)
def salvar_configuracao_smtp(
    payload: SmtpConfigUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(exigir_admin),
):
    config = smtp_config_repository.salvar(
        db,
        host=payload.host,
        port=payload.port,
        usuario=payload.usuario,
        remetente=payload.remetente,
        senha=payload.senha,
        atualizado_por=admin,
    )
    return _to_out(config)


@router.post("/smtp/testar", status_code=status.HTTP_204_NO_CONTENT)
def testar_configuracao_smtp(
    payload: SmtpConfigTestarRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(exigir_admin),
):
    try:
        enviar_email(
            db,
            payload.destinatario,
            "Teste de configuração SMTP",
            "Este é um e-mail de teste do Sistema de Acesso de Médicos. "
            "Se você o recebeu, a configuração SMTP está funcionando.",
        )
    except EmailNaoConfiguradoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Falha ao enviar e-mail de teste: {exc}"
        ) from exc
