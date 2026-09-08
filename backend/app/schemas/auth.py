from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import PerfilUsuario


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    perfil: PerfilUsuario
