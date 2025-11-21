from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Troquei de asyncpg -> psycopg (mais estável no Windows)
DATABASE_URL = settings.DATABASE_URL

# Engine de conexão assíncrona
engine = create_async_engine(
    DATABASE_URL,
    echo=False,           # coloca True se quiser ver as queries no log
    pool_pre_ping=True,   # valida conexões antes de usar
    pool_recycle=1800,    # recicla conexões antigas (30 min)
)

# Session factory para trabalhar com SQLAlchemy em modo async
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # evita lazy load problemático
    autoflush=False,
    autocommit=False,
)

# Base para os models
Base = declarative_base()

# Dependency para injeção de sessão do banco no FastAPI


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
