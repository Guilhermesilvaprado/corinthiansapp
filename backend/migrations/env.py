from app import models  # importa todos os models (__init__.py)
from app.database import Base
from app.core.config import settings
from logging.config import fileConfig
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool

# Garante que o Python ache a pasta /backend/app
BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# Importa settings/Base e models para o Alembic enxergar

# Referência ao alembic.ini
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Usa a URL do .env
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Metadados do ORM
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
