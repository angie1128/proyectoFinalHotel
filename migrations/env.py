from __future__ import with_statement
import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ⚡ Importa tu Settings
from config import settings
from app import db

# Configuración de logging de Alembic
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# MetaData de los modelos para que Alembic detecte las tablas
target_metadata = db.metadata

# 🔑 Fuerza el uso de la URL desde Settings
config.set_main_option("sqlalchemy.url", settings.constructed_database_url)


def run_migrations_offline() -> None:
    """Ejecutar migraciones en modo 'offline'."""
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
    """Ejecutar migraciones en modo 'online'."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
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
