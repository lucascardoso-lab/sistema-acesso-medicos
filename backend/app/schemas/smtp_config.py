from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SmtpConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    host: str
    port: int
    usuario: str
    remetente: EmailStr
    senha_configurada: bool
    updated_at: datetime


class SmtpConfigUpdateRequest(BaseModel):
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(gt=0, le=65535)
    usuario: str = Field(default="", max_length=255)
    remetente: EmailStr
    senha: str | None = Field(default=None, max_length=255)


class SmtpConfigTestarRequest(BaseModel):
    destinatario: EmailStr
