from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.enums import PerfilUsuario
from app.models.solicitacao import Solicitacao
from app.models.user import User
from app.repositories import historico_repository, solicitacao_repository
from app.schemas.historico import HistoricoOut
from app.schemas.solicitacao import (
    ObservacaoRequest,
    RejeitarRequest,
    SolicitacaoDetail,
    SolicitacaoFiltros,
    SolicitacaoListItem,
    SolicitacaoListResponse,
)
from app.services import solicitacao_service

router = APIRouter(prefix="/solicitacoes", tags=["solicitacoes"])


def _to_list_item(solicitacao: Solicitacao) -> SolicitacaoListItem:
    item = SolicitacaoListItem.model_validate(solicitacao)
    item.responsavel_nome = solicitacao.responsavel.nome if solicitacao.responsavel else None
    return item


def _to_detail(solicitacao: Solicitacao) -> SolicitacaoDetail:
    detail = SolicitacaoDetail.model_validate(solicitacao)
    detail.responsavel_nome = solicitacao.responsavel.nome if solicitacao.responsavel else None
    return detail


def _get_solicitacao_ou_404(db: Session, solicitacao_id: int) -> Solicitacao:
    solicitacao = solicitacao_repository.get_by_id(db, solicitacao_id)
    if not solicitacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada")
    return solicitacao


@router.get("", response_model=SolicitacaoListResponse)
def listar_solicitacoes(
    filtros: Annotated[SolicitacaoFiltros, Query()],
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    itens, total = solicitacao_repository.listar(db, filtros)
    return SolicitacaoListResponse(
        items=[_to_list_item(item) for item in itens],
        total=total,
        page=filtros.page,
        page_size=filtros.page_size,
    )


@router.get("/{solicitacao_id}", response_model=SolicitacaoDetail)
def obter_solicitacao(
    solicitacao_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return _to_detail(_get_solicitacao_ou_404(db, solicitacao_id))


@router.get("/{solicitacao_id}/historico", response_model=list[HistoricoOut])
def obter_historico(
    solicitacao_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    _get_solicitacao_ou_404(db, solicitacao_id)
    eventos = historico_repository.listar_por_solicitacao(db, solicitacao_id)
    resultado = []
    for evento in eventos:
        item = HistoricoOut.model_validate(evento)
        item.usuario_nome = evento.usuario.nome if evento.usuario else None
        resultado.append(item)
    return resultado


@router.post("/{solicitacao_id}/iniciar-analise", response_model=SolicitacaoDetail)
def iniciar_analise(
    solicitacao_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    solicitacao = _get_solicitacao_ou_404(db, solicitacao_id)
    solicitacao_service.iniciar_analise(db, solicitacao, user)
    return _to_detail(_get_solicitacao_ou_404(db, solicitacao_id))


@router.post("/{solicitacao_id}/aprovar", response_model=SolicitacaoDetail)
def aprovar(
    solicitacao_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    solicitacao = _get_solicitacao_ou_404(db, solicitacao_id)
    solicitacao_service.aprovar(db, solicitacao, user)
    return _to_detail(_get_solicitacao_ou_404(db, solicitacao_id))


@router.post("/{solicitacao_id}/rejeitar", response_model=SolicitacaoDetail)
def rejeitar(
    solicitacao_id: int,
    payload: RejeitarRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    solicitacao = _get_solicitacao_ou_404(db, solicitacao_id)
    solicitacao_service.rejeitar(db, solicitacao, user, payload.motivo)
    return _to_detail(_get_solicitacao_ou_404(db, solicitacao_id))


@router.patch("/{solicitacao_id}/observacao", response_model=SolicitacaoDetail)
def adicionar_observacao(
    solicitacao_id: int,
    payload: ObservacaoRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    solicitacao = _get_solicitacao_ou_404(db, solicitacao_id)
    solicitacao_service.adicionar_observacao(db, solicitacao, user, payload.observacao_interna)
    return _to_detail(_get_solicitacao_ou_404(db, solicitacao_id))


@router.post("/{solicitacao_id}/marcar-respondida", response_model=SolicitacaoDetail)
def marcar_respondida(
    solicitacao_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    solicitacao = _get_solicitacao_ou_404(db, solicitacao_id)
    solicitacao_service.marcar_respondida(db, solicitacao, user)
    return _to_detail(_get_solicitacao_ou_404(db, solicitacao_id))
