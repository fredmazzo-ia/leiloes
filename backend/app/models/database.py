import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# Diretório data só para SQLite (legado); PostgreSQL usa DATABASE_URL diretamente
if "sqlite" in settings.database_url:
    db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
    if db_path.startswith("."):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        os.makedirs(data_dir, exist_ok=True)

# Aceitar URL padrão (postgresql:// ou postgres://) e converter para o driver async
_db_url = settings.database_url
# asyncpg não usa sslmode=disable na URL; tratar e passar ssl no connect_args
_connect_args = {}
if "sslmode=disable" in _db_url:
    _db_url = _db_url.replace("?sslmode=disable", "").replace("&sslmode=disable", "")
    if _db_url.endswith("?"):
        _db_url = _db_url[:-1]
    _connect_args["ssl"] = False
if _db_url.startswith("postgresql://") and "+asyncpg" not in _db_url:
    _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _db_url.startswith("postgres://"):
    _db_url = "postgresql+asyncpg://" + _db_url[len("postgres://") :]

engine = create_async_engine(
    _db_url,
    echo=False,
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    from . import schemas  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
