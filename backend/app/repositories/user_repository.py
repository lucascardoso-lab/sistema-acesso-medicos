from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.user import User


def get_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def get_by_login(db: Session, login: str) -> User | None:
    return db.execute(select(User).where(User.login == login)).scalar_one_or_none()


def get_by_login_ou_email(db: Session, valor: str) -> User | None:
    return db.execute(
        select(User).where(or_(User.email == valor, User.login == valor))
    ).scalar_one_or_none()


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def listar(db: Session) -> list[User]:
    return list(db.execute(select(User).order_by(User.nome)).scalars().all())
