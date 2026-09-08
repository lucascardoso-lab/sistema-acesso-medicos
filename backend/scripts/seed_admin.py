"""Cria ou atualiza a senha do usuário administrador inicial.

Uso:
    python -m scripts.seed_admin --nome "Nome" --email admin@exemplo.com --senha "senha-forte"
"""

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models.enums import PerfilUsuario
from app.models.user import User
from app.repositories import user_repository


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria ou atualiza o usuário administrador inicial")
    parser.add_argument("--nome", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--senha", required=True)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        user = user_repository.get_by_email(db, args.email)
        if user:
            user.password_hash = hash_password(args.senha)
            user.nome = args.nome
            user.perfil = PerfilUsuario.ADMINISTRADOR
            user.ativo = True
            print(f"Usuário {args.email} atualizado.")
        else:
            user = User(
                nome=args.nome,
                email=args.email,
                password_hash=hash_password(args.senha),
                perfil=PerfilUsuario.ADMINISTRADOR,
                ativo=True,
            )
            db.add(user)
            print(f"Usuário {args.email} criado.")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
