import os
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Get logger
logger = logging.getLogger("ai_assistant")

# Set up async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
logger.debug(f"Async engine created with DATABASE_URL: {DATABASE_URL}")

# Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        logger.debug("Database session started")
        yield session
        logger.debug("Database session closed")

# Connection test function
async def test_connection():
    logger.debug("Testing database connection...")
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
    except Exception as e:
        logger.exception("Database connection test failed")
        raise
