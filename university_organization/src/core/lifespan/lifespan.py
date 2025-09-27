from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.lifespan.permissions_sync import sync_permissions

from core.utils.database import db_helper
from core.config import LOG_DEFAULT_FORMAT
import logging

logging.basicConfig(
    level=logging.INFO,
    format=LOG_DEFAULT_FORMAT
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    logging.info("🚀 Lifespan startup...") 
    
    async with db_helper.session_factory() as session:
        await sync_permissions(app, session)

    yield
    
    logging.info("🛑 Lifespan shutdown...")
    await db_helper.dispose()
