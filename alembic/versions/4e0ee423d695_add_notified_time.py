"""Add notified time

Revision ID: 4e0ee423d695
Revises: None
Create Date: 2012-08-07 21:59:49.914456

"""

# revision identifiers, used by Alembic.
revision = '4e0ee423d695'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('snipe', sa.Column('notified', sa.DateTime))


def downgrade():
    op.drop_column('snipe', 'notified')
