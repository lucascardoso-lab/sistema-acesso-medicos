import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings

settings = get_settings()


def _fernet() -> Fernet:
    chave = base64.urlsafe_b64encode(hashlib.sha256(settings.secret_key.encode()).digest())
    return Fernet(chave)


def criptografar(valor: str) -> str:
    return _fernet().encrypt(valor.encode()).decode()


def descriptografar(valor_criptografado: str) -> str:
    try:
        return _fernet().decrypt(valor_criptografado.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Não foi possível descriptografar o valor armazenado") from exc
