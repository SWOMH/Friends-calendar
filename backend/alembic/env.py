from logging.config import fileConfig
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import asyncio

from database.base import Base
from config.constants import DEV_CONSTANT
from sqlalchemy.ext.asyncio import create_async_engine

from database.models.user_models import *
from database.models.celendar import *

env_file = os.getenv("APP_ENV", "dev")
env_path = Path(__file__).parents[1] / f".env.{env_file}"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv(Path(__file__).parents[1] / ".env")

db_url = os.getenv("DATABASE_URL", DEV_CONSTANT.DATABASE_URL)
config = context.config
config.set_main_option('sqlalchemy.url', db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    connectable = create_async_engine(config.get_main_option("sqlalchemy.url"))

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        task = loop.create_task(run_async_migrations())
        task.add_done_callback(lambda t: loop.stop())
        loop.run_forever()
    else:
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
