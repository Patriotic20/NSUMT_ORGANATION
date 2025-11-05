from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession 

from .schemas import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupGet,
)
from .service import GroupService 

from core.utils.database import db_helper
from core.models.user import User
from core.schemas.get_all import GetAll
from auth.utils.dependencies import require_permission

router = APIRouter(
    tags=["Group"],
    prefix="/groups",
)

def get_group_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return GroupService(session=session)

@router.post("/create", response_model=GroupResponse)
async def create(
    create_data: GroupCreate,
    service: GroupService = Depends(get_group_service),
    _: User = Depends(require_permission("create:groups"))
    ):
    return await service.create(create_data=create_data)


@router.get("")
async def get_all(
    search: str | None = None,
    pagination: GetAll = Depends(),
    service: GroupService = Depends(get_group_service),
    _: User = Depends(require_permission("read:groups"))
    ):
    return await service.get_all(pagination=pagination, search = search)


@router.get("/get/{id}", response_model=GroupResponse)
async def get_by_id(
    group_get: GroupGet = Depends(),
    service: GroupService = Depends(get_group_service),
    _: User = Depends(require_permission("read:groups"))
    ):
    return await service.get_by_id(group_get=group_get)


@router.put("/update/{id}", response_model=GroupResponse)
async def update(
    update_data: GroupUpdate,
    group_get: GroupGet = Depends(),
    service: GroupService = Depends(get_group_service),
    _: User = Depends(require_permission("update:groups"))
    ):
    return await service.update(group_get=group_get, update_data=update_data)


@router.delete("/delete/{id}")
async def delete(
    group_get: GroupGet = Depends(),
    service: GroupService = Depends(get_group_service),
    _: User = Depends(require_permission("delete:groups"))
    ):
    await service.delete(group_get=group_get)
    return {"message": "Group deleted successfully"}
