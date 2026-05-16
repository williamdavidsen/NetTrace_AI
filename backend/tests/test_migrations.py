from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_head_creates_network_tables(tmp_path: Path) -> None:
    database_path = tmp_path / "migration-check.db"
    database_url = f"sqlite:///{database_path}"

    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(alembic_config, "head")

    engine = create_engine(database_url)
    inspector = inspect(engine)

    assert {"scans", "packet_events", "alerts"}.issubset(set(inspector.get_table_names()))
