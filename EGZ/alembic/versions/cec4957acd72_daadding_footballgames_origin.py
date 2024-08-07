"""Daadding_footballgames_origin

Revision ID: cec4957acd72
Revises: 10fd3f720863
Create Date: 2024-08-05 19:55:12.047213

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cec4957acd72'
down_revision = '10fd3f720863'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tournaments_football_games', sa.Column('origin', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tournaments_football_games', 'origin')
    # ### end Alembic commands ###
