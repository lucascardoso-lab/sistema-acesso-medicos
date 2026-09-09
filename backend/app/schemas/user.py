from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import PerfilUsuario


LOGIN_PATTERN = r"^[a-zA-Z0-9._-]{3,50}$"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    login: str
    email: EmailStr
    perfil: PerfilUsuario
    ativo: bool


class UserCreateRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    login: str = Field(pattern=LOGIN_PATTERN)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=100)
    perfil: PerfilUsuario


class UserUpdateRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=150)
    login: str | None = Field(default=None, pattern=LOGIN_PATTERN)
    email: EmailStr | None = None
    perfil: PerfilUsuario | None = None
    ativo: bool | None = None


class RedefinirSenhaRequest(BaseModel):
    senha: str = Field(min_length=8, max_length=100)
