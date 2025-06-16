# Entry point for FastAPI application
from fastapi import FastAPI
from app.api.routes import router
from app.api.chat import router
from contextlib import asynccontextmanager
from app.db.connection import test_connection
from app.utils.setup_logger import setup_logger
logger = setup_logger("ai_assistant")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting FastAPI application...")
    try:
        await test_connection()
        logger.info("✅ Database connection successful.")
    except Exception as e:
        logger.exception("❌ Database connection failed: %s", str(e))

    yield  # This is where the app runs

    # Shutdown
    logger.info("👋 Shutting down FastAPI application.")

app = FastAPI(lifespan=lifespan, title="ai_assistant")


app.include_router(router, prefix="/chat", tags=["chat"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "AI assistant is up and running..."}
