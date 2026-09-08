from collections.abc import Callable

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.enums import PerfilUsuario
from app.models.user import User
from app.repositories import user_repository

COOKIE_NAME = "access_token"


def get_current_user(
    access_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado"
    )
    if not access_token:
        raise credentials_error

    payload = decode_access_token(access_token)
    if not payload or "sub" not in payload:
        raise credentials_error

    user = user_repository.get_by_id(db, int(payload["sub"]))
    if not user or not user.ativo:
        raise credentials_error

    return user


def require_perfil(*perfis: PerfilUsuario) -> Callable[[User], User]:
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.perfil not in perfis:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        return user

    return dependency
