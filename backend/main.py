import uvicorn
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from foundation_models.routes import router as foundation_models_router
from chat_playground.routes import router as chat_playground_router
from text_playground.routes import router as text_playground_router
from image_playground.routes import router as image_playground_router
from health.routes import router as health_router

# Configure logging with environment variable support
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"Starting application with log level: {log_level}")

app = FastAPI()

app.include_router(health_router)
app.include_router(foundation_models_router)
app.include_router(chat_playground_router)
app.include_router(text_playground_router)
app.include_router(image_playground_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_CORS_ORIGINS,
    allow_methods=config.ALLOWED_CORS_METHODS,
    allow_headers=config.ALLOWED_CORS_HEADERS
)

if __name__ == "__main__":
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, log_level="info")