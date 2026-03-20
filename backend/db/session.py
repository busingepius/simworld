import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from core.config import get_settings

settings = get_settings()

# Celery workers call asyncio.run() per task, creating a new event loop each time.
# A shared connection pool would hold connections tied to a previous (closed) loop,
# causing "Future attached to a different loop" errors. NullPool avoids this by
# never reusing connections across calls.
_pool_class = NullPool if os.environ.get("CELERY_WORKER") else None

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    **( {"poolclass": NullPool} if _pool_class else {} ),
)

# Async session factory
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI that provides a transactional async database session.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
