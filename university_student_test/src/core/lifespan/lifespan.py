from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.lifespan.permissions_sync import sync_permissions

from core.database.db_helper import db_helper
from core.config import LOG_DEFAULT_FORMAT
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format=LOG_DEFAULT_FORMAT
)


UPLOAD_DIR = "uploads"

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    logging.info("🚀 Lifespan startup...") 
    
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        print(f"Created main folder: {UPLOAD_DIR}")
    
    await sync_permissions(app)

    yield
    
    
    logging.info("🛑 Lifespan shutdown...")
    await db_helper.dispose()
