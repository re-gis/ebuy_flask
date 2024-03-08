"""adding columns

Revision ID: 87a0fa6e61b0
Revises: 7d686d65e26d
Create Date: 2024-03-08 13:12:48.325705

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87a0fa6e61b0'
down_revision = '7d686d65e26d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('carts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total_quantity', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('total_price', sa.Float(), nullable=True))

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['name'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('carts', schema=None) as batch_op:
        batch_op.drop_column('total_price')
        batch_op.drop_column('total_quantity')

    # ### end Alembic commands ###
