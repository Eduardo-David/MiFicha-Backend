"""
Add last_profile_update to user
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c7b2e91f0a12'
down_revision = '573fd07f9fe0'
depends_on = None


def upgrade():
    op.add_column(
        'user',
        sa.Column('last_profile_update', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )


def downgrade():
    op.drop_column('user', 'last_profile_update')

