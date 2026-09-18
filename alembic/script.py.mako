"""
${message}
"""

from alembic import op
import sqlalchemy as sa
from alembic import context
import sqlalchemy.dialects.postgresql as pg

# revision identifiers, used by Alembic.
revision = '${up_revision}'
down_revision = ${repr(down_revision)}
depends_on = ${repr(depends_on)}



def upgrade():
    ${upgrades if upgrades else 'pass'}


def downgrade():
    ${downgrades if downgrades else 'pass'}
