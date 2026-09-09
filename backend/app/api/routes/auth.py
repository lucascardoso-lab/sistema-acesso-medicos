from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import COOKIE_NAME, get_current_user
from app.core.config import get_settings
from app.core.limiter import limiter
from app.core.security import create_access_token, verify_password
from app.database.session import get_db
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth import LoginRequest
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=UserOut)
@limiter.limit("10/minute")
def login(request: Request, response: Response, credentials: LoginRequest, db: Session = Depends(get_db)):
    user = user_repository.get_by_login_ou_email(db, credentials.login_ou_email)
    if not user or not user.ativo or not verify_password(credentials.senha, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Login/e-mail ou senha inválidos"
        )

    token = create_access_token(subject=str(user.id))
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
