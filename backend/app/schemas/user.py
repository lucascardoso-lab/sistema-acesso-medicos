from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import PerfilUsuario


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    perfil: PerfilUsuario
    ativo: bool


class UserCreateRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=100)
    perfil: PerfilUsuario


class UserUpdateRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=150)
    perfil: PerfilUsuario | None = None
    ativo: bool | None = None


class RedefinirSenhaRequest(BaseModel):
    senha: str = Field(min_length=8, max_length=100)
