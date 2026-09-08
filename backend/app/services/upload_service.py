from pathlib import Path

from app.core.config import get_settings
from app.utils.file_validation import gerar_nome_aleatorio

settings = get_settings()

SUBPASTA_DOCUMENTO = "documentos"
SUBPASTA_FOTO = "fotos"


def _diretorio(subpasta: str) -> Path:
    caminho = settings.upload_dir / subpasta
    caminho.mkdir(parents=True, exist_ok=True)
    return caminho


def salvar_arquivo(conteudo: bytes, extensao: str, subpasta: str) -> str:
    nome = gerar_nome_aleatorio(extensao)
    destino = _diretorio(subpasta) / nome
    destino.write_bytes(conteudo)
    return f"{subpasta}/{nome}"


def caminho_absoluto(caminho_relativo: str) -> Path:
    caminho = (settings.upload_dir / caminho_relativo).resolve()
    upload_dir_resolvido = settings.upload_dir.resolve()
    if upload_dir_resolvido not in caminho.parents and caminho != upload_dir_resolvido:
        raise ValueError("Caminho de arquivo inválido")
    return caminho
