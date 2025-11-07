import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from dotenv import load_dotenv
from app.database.base import Base
from app.utils.logger import get_logger

logger = get_logger("session")

# Load .env file
load_dotenv()

# --- Database URL ---
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./data/ai_tutor.db"  # Default fallback
)

# Ensure data directory exists for SQLite
if DATABASE_URL.startswith("sqlite"):
    os.makedirs("./data", exist_ok=True)

logger.info(f"📦 Using database: {DATABASE_URL}")

# --- Engine Configuration ---
engine = create_async_engine(
    DATABASE_URL,
    echo=False,          # Set to True for SQL debugging
    future=True,
    pool_pre_ping=True,
)

# --- Session Factory ---
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# ✅ Import models AFTER Base is defined
from app.models import *  # Ensures all tables are registered before init_db()

# --- Dependency for FastAPI ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize the database and create all tables."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("✅ Database tables created successfully.")

    # Optional: verify which tables were created safely
    from sqlalchemy import inspect

    def get_tables(sync_conn):
        inspector = inspect(sync_conn)
        return inspector.get_table_names()

    async with engine.connect() as conn:
        tables = await conn.run_sync(get_tables)
        logger.info(f"📚 Tables in DB: {tables}")

