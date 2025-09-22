from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse
)
from .service import PermissionService

from core.utils.database import db_helper
from core.schemas.get_all import GetAll
from core.models.user import User

from auth.utils.dependencies import require_permission

router = APIRouter(
    tags=["Permission"],
    prefix="/permissions"
)


def get_permission_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return PermissionService(session=session)

@router.post("/create" , response_model=PermissionResponse)
async def create(
    create_data: PermissionCreate,
    service: PermissionService = Depends(get_permission_service)  
):
    return await service.create(create_data=create_data)


@router.post("/sync")
async def sync_permissions(
    perms: list[PermissionCreate],
    service: PermissionService = Depends(get_permission_service),
    # _: User = Depends(require_permission("create:permissions"))
):
    return await service.sync_permissions(perms=perms)

@router.get("")
async def get_all(
    pagination: GetAll = Depends(),
    service: PermissionService = Depends(get_permission_service)
):
    return await service.get_all(pagination=pagination)


@router.get("/get/{id}")
async def get_by_id(
    id: int,
    service: PermissionService = Depends(get_permission_service)
):
    return await service.get_by_id(id=id)


@router.patch("/update/{id}")
async def update(
    id: int,
    update_data: PermissionUpdate,
    service: PermissionService = Depends(get_permission_service)
):
    return await service.update(id=id, update_data=update_data)


@router.delete("/delete/{id}")
async def delete(
    id: int,
    service: PermissionService = Depends(get_permission_service)
):
    return await service.delete(id=id)
