from fastapi import APIRouter , Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import ChairService
from .schemas import (
    ChairCreate,
    ChairUpdate,
    ChairResponse,
    ChairGet
)

from core.utils.database import db_helper
from core.models import User
from core.schemas.get_all import GetAll

from auth.utils.dependencies import require_permission

router = APIRouter(
    tags=["Chair"],
    prefix="/chairs",
)

def get_chair_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return ChairService(session=session)

@router.post("/create")
async def create(
    create_data: ChairCreate,
    service: ChairService = Depends(get_chair_service),
    _: User = Depends(require_permission("create:chairs"))
    ):
    return await service.create(create_data=create_data)
     


@router.get("", response_model=list[ChairResponse])
async def get_all(
    pagination: GetAll = Depends(),
    service: ChairService = Depends(get_chair_service),
    _: User = Depends(require_permission("read:chairs"))
    ):
    return await service.get_all(pagination=pagination)


@router.get("/get/{id}", response_model=ChairResponse)
async def get_by_id(
    chair_get: ChairGet = Depends(),
    service: ChairService = Depends(get_chair_service),
    _: User = Depends(require_permission("read:chairs"))
    ):
    return await service.get_by_id(chair_get=chair_get)
    

@router.put("/update/{id}", response_model=ChairResponse)
async def update(
    update_data: ChairUpdate,
    chair_get: ChairGet = Depends(),
    service: ChairService = Depends(get_chair_service),
    _: User = Depends(require_permission("update:chairs"))
    ):
    return await service.update(chair_get=chair_get, update_data=update_data)


@router.delete("/delete/{id}")
async def delete(
    chair_get: ChairGet = Depends(),
    service: ChairService = Depends(get_chair_service),
    _: User = Depends(require_permission("delete:chairs"))
    ):
    await service.delete(chair_get=chair_get)
    return {"message": "Chair deleted successfully"}
