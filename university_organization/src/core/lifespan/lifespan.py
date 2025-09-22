from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.lifespan.permissions_sync import sync_permissions

from core.utils.database import db_helper



@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # run_migrations()
    


    async with db_helper.session_factory() as session:
        await sync_permissions(app, session)

    yield


    await db_helper.dispose()
