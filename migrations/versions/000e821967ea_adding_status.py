"""Adding status

Revision ID: 000e821967ea
Revises: 97f487506182
Create Date: 2024-03-11 15:46:57.043714

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '000e821967ea'
down_revision = '97f487506182'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('locations', schema=None) as batch_op:
        batch_op.drop_constraint('locations_country_key', type_='unique')
        batch_op.drop_constraint('locations_district_key', type_='unique')
        batch_op.drop_constraint('locations_province_key', type_='unique')
        batch_op.drop_constraint('locations_sector_key', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('locations', schema=None) as batch_op:
        batch_op.create_unique_constraint('locations_sector_key', ['sector'])
        batch_op.create_unique_constraint('locations_province_key', ['province'])
        batch_op.create_unique_constraint('locations_district_key', ['district'])
        batch_op.create_unique_constraint('locations_country_key', ['country'])

    # ### end Alembic commands ###
