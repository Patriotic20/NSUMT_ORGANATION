from alembic import command
from alembic.config import Config
from pathlib import Path

def run_migrations():
    
    alembic_cfg = Config(str(Path(__file__).parent.parent / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")                         
