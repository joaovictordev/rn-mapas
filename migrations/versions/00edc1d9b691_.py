"""empty message

Revision ID: 00edc1d9b691
Revises: 97947bd04a3d
Create Date: 2019-03-17 11:10:11.765400

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00edc1d9b691'
down_revision = '97947bd04a3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('maps',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('send_date', sa.DateTime(), nullable=False),
    sa.Column('aproved_date', sa.DateTime(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('maps')
    # ### end Alembic commands ###
