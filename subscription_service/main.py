from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .utils.logger_config import setup_logger


logger = setup_logger("subscription_service")

app = FastAPI(title="subscription_service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    logger.info("Subscription Service is running...")
    return {"status": "ok"}
