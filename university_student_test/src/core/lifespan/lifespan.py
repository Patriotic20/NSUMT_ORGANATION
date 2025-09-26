from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.lifespan.permissions_sync import sync_permissions

from core.database.db_helper import db_helper
import os

UPLOAD_DIR = "uploads"

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        print(f"Created main folder: {UPLOAD_DIR}")
    
    await sync_permissions(app)

    yield


    await db_helper.dispose()
