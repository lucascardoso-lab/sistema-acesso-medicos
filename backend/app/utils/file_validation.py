import uuid

import magic
from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings

settings = get_settings()

EXTENSOES_DOCUMENTO = {".pdf", ".jpg", ".jpeg", ".png"}
EXTENSOES_FOTO = {".jpg", ".jpeg", ".png"}

MIME_PERMITIDOS = {
    ".pdf": {"application/pdf"},
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".png": {"image/png"},
}


def extrair_extensao(filename: str) -> str:
    partes = filename.rsplit(".", 1)
    if len(partes) != 2:
        return ""
    return f".{partes[1].lower()}"


async def validar_e_ler_upload(
    arquivo: UploadFile, *, extensoes_permitidas: set[str]
) -> tuple[bytes, str]:
    extensao = extrair_extensao(arquivo.filename or "")
    if extensao not in extensoes_permitidas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensão de arquivo não permitida: {extensao or 'desconhecida'}",
        )

    conteudo = await arquivo.read()
    if len(conteudo) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo vazio")
    if len(conteudo) > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo excede o tamanho máximo de {settings.max_upload_size} bytes",
        )

    mime_detectado = magic.from_buffer(conteudo, mime=True)
    if mime_detectado not in MIME_PERMITIDOS.get(extensao, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não corresponde ao conteúdo enviado ({mime_detectado})",
        )

    return conteudo, extensao


def gerar_nome_aleatorio(extensao: str) -> str:
    return f"{uuid.uuid4().hex}{extensao}"
