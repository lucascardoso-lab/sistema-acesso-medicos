from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    login_ou_email: str = Field(min_length=3, max_length=150)
    senha: str
