"""adiciona campo login em users

Revision ID: a3a823258a92
Revises: cec60c10d638
Create Date: 2026-09-08 20:28:28.742834

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3a823258a92'
down_revision = 'cec60c10d638'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('login', sa.String(length=50), nullable=True))

    # Backfill: usuarios existentes recebem a parte do e-mail antes do "@"
    # como login provisorio, para permitir a coluna NOT NULL + UNIQUE abaixo.
    # Deve ser revisado/ajustado manualmente pelo administrador apos o deploy.
    conn = op.get_bind()
    conn.execute(sa.text(
        "UPDATE users SET login = SUBSTRING_INDEX(email, '@', 1) WHERE login IS NULL"
    ))

    op.alter_column('users', 'login', existing_type=sa.String(length=50), nullable=False)
    op.create_index(op.f('ix_users_login'), 'users', ['login'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_login'), table_name='users')
    op.drop_column('users', 'login')
