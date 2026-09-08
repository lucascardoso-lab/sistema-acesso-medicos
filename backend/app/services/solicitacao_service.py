from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import StatusSolicitacao
from app.models.solicitacao import Solicitacao
from app.models.user import User
from app.repositories import historico_repository


def _erro_status_invalido(atual: StatusSolicitacao, esperado: StatusSolicitacao) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Ação inválida: status atual é '{atual.value}', esperado '{esperado.value}'",
    )


def iniciar_analise(db: Session, solicitacao: Solicitacao, usuario: User) -> Solicitacao:
    if solicitacao.status != StatusSolicitacao.PENDENTE:
        raise _erro_status_invalido(solicitacao.status, StatusSolicitacao.PENDENTE)

    status_anterior = solicitacao.status
    solicitacao.status = StatusSolicitacao.EM_ANALISE
    solicitacao.responsavel_id = usuario.id
    solicitacao.analise_iniciada_at = datetime.now(timezone.utc)

    historico_repository.registrar(
        db,
        solicitacao_id=solicitacao.id,
        usuario=usuario,
        acao="Análise iniciada",
        status_anterior=status_anterior.value,
        status_novo=solicitacao.status.value,
    )
    db.commit()
    db.refresh(solicitacao)
    return solicitacao


def aprovar(db: Session, solicitacao: Solicitacao, usuario: User) -> Solicitacao:
    if solicitacao.status != StatusSolicitacao.EM_ANALISE:
        raise _erro_status_invalido(solicitacao.status, StatusSolicitacao.EM_ANALISE)

    status_anterior = solicitacao.status
    solicitacao.status = StatusSolicitacao.APROVADA
    solicitacao.analisado_at = datetime.now(timezone.utc)

    historico_repository.registrar(
        db,
        solicitacao_id=solicitacao.id,
        usuario=usuario,
        acao="Solicitação aprovada",
        status_anterior=status_anterior.value,
        status_novo=solicitacao.status.value,
    )
    db.commit()
    db.refresh(solicitacao)
    return solicitacao


def rejeitar(db: Session, solicitacao: Solicitacao, usuario: User, motivo: str) -> Solicitacao:
    if solicitacao.status != StatusSolicitacao.EM_ANALISE:
        raise _erro_status_invalido(solicitacao.status, StatusSolicitacao.EM_ANALISE)

    status_anterior = solicitacao.status
    solicitacao.status = StatusSolicitacao.REJEITADA
    solicitacao.motivo_rejeicao = motivo
    solicitacao.analisado_at = datetime.now(timezone.utc)

    historico_repository.registrar(
        db,
        solicitacao_id=solicitacao.id,
        usuario=usuario,
        acao="Solicitação rejeitada",
        status_anterior=status_anterior.value,
        status_novo=solicitacao.status.value,
        descricao=motivo,
    )
    db.commit()
    db.refresh(solicitacao)
    return solicitacao


def adicionar_observacao(db: Session, solicitacao: Solicitacao, usuario: User, observacao: str) -> Solicitacao:
    solicitacao.observacao_interna = observacao

    historico_repository.registrar(
        db,
        solicitacao_id=solicitacao.id,
        usuario=usuario,
        acao="Observação interna adicionada",
        descricao=observacao,
    )
    db.commit()
    db.refresh(solicitacao)
    return solicitacao


def marcar_respondida(db: Session, solicitacao: Solicitacao, usuario: User) -> Solicitacao:
    if solicitacao.status not in (StatusSolicitacao.APROVADA, StatusSolicitacao.REJEITADA):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ação inválida: solicitação precisa estar aprovada ou rejeitada",
        )

    status_anterior = solicitacao.status
    solicitacao.status = StatusSolicitacao.RESPONDIDA
    solicitacao.respondido_at = datetime.now(timezone.utc)

    historico_repository.registrar(
        db,
        solicitacao_id=solicitacao.id,
        usuario=usuario,
        acao="Solicitação marcada como respondida",
        status_anterior=status_anterior.value,
        status_novo=solicitacao.status.value,
    )
    db.commit()
    db.refresh(solicitacao)
    return solicitacao
