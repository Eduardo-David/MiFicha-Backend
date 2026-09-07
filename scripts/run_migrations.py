from alembic.config import Config
from alembic import command
import os

alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))

if __name__ == '__main__':
    command.upgrade(alembic_cfg, 'head')
