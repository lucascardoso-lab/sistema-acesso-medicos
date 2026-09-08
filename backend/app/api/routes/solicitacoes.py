from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.limiter import limiter
from app.database.session import get_db
from app.models.solicitacao import Solicitacao
from app.models.user import User
from app.repositories import historico_repository, solicitacao_repository
from app.schemas.historico import HistoricoOut
from app.schemas.solicitacao import (
    EnviarEmailRequest,
    ObservacaoRequest,
    RejeitarRequest,
    SolicitacaoCreatedResponse,
    SolicitacaoDetail,
    SolicitacaoFiltros,
    SolicitacaoListItem,
    SolicitacaoListResponse,
)
from app.services import solicitacao_service, upload_service
from app.utils.file_validation import EXTENSOES_DOCUMENTO, EXTENSOES_FOTO, validar_e_ler_upload

router = APIRouter(prefix="/solicitacoes", tags=["solicitacoes"])

CONSENTIMENTO_VERSAO_ATUAL = "1.0"
TENTATIVAS_PROTOCOLO = 3


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


@router.post("", response_model=SolicitacaoCreatedResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def criar_solicitacao(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    nome_completo: Annotated[str, Form(min_length=3, max_length=150)],
    conselho: Annotated[str, Form(min_length=2, max_length=20)],
    numero_conselho: Annotated[str, Form(min_length=1, max_length=30)],
    uf_conselho: Annotated[str, Form(min_length=2, max_length=2)],
    especialidade: Annotated[str, Form(min_length=2, max_length=100)],
    email: Annotated[EmailStr, Form()],
    telefone: Annotated[str, Form(min_length=8, max_length=20)],
    consentimento_lgpd: Annotated[bool, Form()],
    documento: Annotated[UploadFile, File()],
    foto_documento: Annotated[UploadFile, File()],
):
    if not consentimento_lgpd:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="É necessário aceitar o consentimento de tratamento de dados",
        )

    conteudo_documento, extensao_documento = await validar_e_ler_upload(
        documento, extensoes_permitidas=EXTENSOES_DOCUMENTO
    )
    conteudo_foto, extensao_foto = await validar_e_ler_upload(
        foto_documento, extensoes_permitidas=EXTENSOES_FOTO
    )

    documento_path = upload_service.salvar_arquivo(
        conteudo_documento, extensao_documento, upload_service.SUBPASTA_DOCUMENTO
    )
    foto_path = upload_service.salvar_arquivo(conteudo_foto, extensao_foto, upload_service.SUBPASTA_FOTO)

    for tentativa in range(TENTATIVAS_PROTOCOLO):
        protocolo = solicitacao_repository.gerar_protocolo(db)
        solicitacao = Solicitacao(
            protocolo=protocolo,
            nome_completo=nome_completo,
            conselho=conselho,
            numero_conselho=numero_conselho,
            uf_conselho=uf_conselho.upper(),
            especialidade=especialidade,
            email=email,
            telefone=telefone,
            documento_path=documento_path,
            selfie_documento_path=foto_path,
            consentimento_lgpd=True,
            consentimento_versao=CONSENTIMENTO_VERSAO_ATUAL,
            consentimento_at=datetime.now(timezone.utc),
        )
        db.add(solicitacao)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            if tentativa == TENTATIVAS_PROTOCOLO - 1:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Não foi possível gerar o protocolo, tente novamente",
                ) from None
            continue
        break

    historico_repository.registrar(
        db,
        solicitacao_id=solicitacao.id,
        usuario=None,
        acao="Solicitação criada",
        status_novo=solicitacao.status.value,
    )
    db.commit()
    return SolicitacaoCreatedResponse(protocolo=solicitacao.protocolo)


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


@router.get("/{solicitacao_id}/documentos/{tipo}")
def obter_documento(
    solicitacao_id: int,
    tipo: Literal["documento", "foto"],
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    solicitacao = _get_solicitacao_ou_404(db, solicitacao_id)
    caminho_relativo = solicitacao.documento_path if tipo == "documento" else solicitacao.selfie_documento_path

    try:
        caminho = upload_service.caminho_absoluto(caminho_relativo)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado") from None

    if not caminho.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado")

    return FileResponse(caminho)


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


@router.post("/{solicitacao_id}/enviar-email", response_model=SolicitacaoDetail)
def enviar_email_resposta(
    solicitacao_id: int,
    payload: EnviarEmailRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    solicitacao = _get_solicitacao_ou_404(db, solicitacao_id)
    solicitacao_service.enviar_email_resposta(db, solicitacao, user, payload.mensagem)
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
