"""
Alembic Migration Ortam Konfigürasyonu

Alembic CLI tarafından kullanılır. Modelleri otomatik algılar
ve migration dosyaları üretir.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from src.db.models import Base
from src.core.config import settings

# Alembic Config objesi
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model metadata — otomatik migration için gerekli
target_metadata = Base.metadata

# Dinamik URL (.env'den)
config.set_main_option("sqlalchemy.url", settings.postgres.sync_url)


def run_migrations_offline() -> None:
    """
    Offline modda migration çalıştırır.
    Veritabanına bağlanmadan SQL dosyası üretir.
    """
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
    """
    Online modda migration çalıştırır.
    Veritabanına bağlanarak doğrudan uygular.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
