# Entry point for FastAPI application
from fastapi import FastAPI
from app.routes import router
from contextlib import asynccontextmanager
from app.db.connection import test_connection
from app.utils.setup_logger import setup_logger
import logging

logger = setup_logger(name="ai_assistant",level=logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting FastAPI application...")
    try:
        await test_connection()
        logger.info("Database connection successful.")
    except Exception as e:
        logger.exception("Database connection failed: %s", str(e))

    yield  # This is where the app runs

    # Shutdown
    logger.info("Shutting down FastAPI application.")

app = FastAPI(lifespan=lifespan, title="ai_assistant")

app.include_router(router, prefix="/chat", tags=["chat"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "AI assistant is up and running..."}
