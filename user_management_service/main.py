from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .utils.logger_config import setup_logger


logger = setup_logger("user_management_service")

app = FastAPI(title="user_management_service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    logger.info("User Management service is running...")
    return {"status": "ok"}
