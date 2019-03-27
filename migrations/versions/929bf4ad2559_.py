"""empty message

Revision ID: 929bf4ad2559
Revises: e7e9946f3cc0
Create Date: 2019-03-22 22:49:58.242341

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '929bf4ad2559'
down_revision = 'e7e9946f3cc0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('maps', 'aproved_date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('maps', sa.Column('aproved_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
