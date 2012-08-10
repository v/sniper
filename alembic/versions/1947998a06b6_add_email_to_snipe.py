"""Add email to snipe

Revision ID: 1947998a06b6
Revises: 4e0ee423d695
Create Date: 2012-08-09 14:27:52.434843

"""

# revision identifiers, used by Alembic.
revision = '1947998a06b6'
down_revision = '4e0ee423d695'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('snipe', sa.Column('email', sa.String(255)))


def downgrade():
    op.drop_column('snipe', 'email')
