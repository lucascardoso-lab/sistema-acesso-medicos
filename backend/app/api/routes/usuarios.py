from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_perfil
from app.core.security import hash_password
from app.database.session import get_db
from app.models.enums import PerfilUsuario
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import RedefinirSenhaRequest, UserCreateRequest, UserOut, UserUpdateRequest

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

exigir_admin = require_perfil(PerfilUsuario.ADMINISTRADOR)


def _get_usuario_ou_404(db: Session, user_id: int) -> User:
    usuario = user_repository.get_by_id(db, user_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return usuario


@router.get("", response_model=list[UserOut])
def listar_usuarios(db: Session = Depends(get_db), _admin: User = Depends(exigir_admin)):
    return user_repository.listar(db)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(exigir_admin),
):
    if user_repository.get_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")
    if user_repository.get_by_login(db, payload.login):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login já cadastrado")

    usuario = User(
        nome=payload.nome,
        login=payload.login,
        email=payload.email,
        password_hash=hash_password(payload.senha),
        perfil=payload.perfil,
        ativo=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{user_id}", response_model=UserOut)
def atualizar_usuario(
    user_id: int,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(exigir_admin),
):
    usuario = _get_usuario_ou_404(db, user_id)

    if usuario.id == admin.id and payload.ativo is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Não é possível desativar o próprio usuário"
        )

    if payload.login is not None and payload.login != usuario.login:
        existente = user_repository.get_by_login(db, payload.login)
        if existente and existente.id != usuario.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login já cadastrado")
        usuario.login = payload.login
    if payload.email is not None and payload.email != usuario.email:
        existente = user_repository.get_by_email(db, payload.email)
        if existente and existente.id != usuario.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")
        usuario.email = payload.email
    if payload.nome is not None:
        usuario.nome = payload.nome
    if payload.perfil is not None:
        usuario.perfil = payload.perfil
    if payload.ativo is not None:
        usuario.ativo = payload.ativo

    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/{user_id}/redefinir-senha", response_model=UserOut)
def redefinir_senha(
    user_id: int,
    payload: RedefinirSenhaRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(exigir_admin),
):
    usuario = _get_usuario_ou_404(db, user_id)
    usuario.password_hash = hash_password(payload.senha)
    db.commit()
    db.refresh(usuario)
    return usuario
