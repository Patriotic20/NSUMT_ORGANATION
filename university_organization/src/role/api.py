from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.utils.database import db_helper
from .service import RoleService
from .schemas import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RolePermission
)

from core.models.user import User
from core.schemas.get_all import GetAll
from auth.utils.dependencies import require_permission

router = APIRouter(
    tags=["Role"],
    prefix="/roles",
)

def get_role_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return RoleService(session=session)


@router.post("/create", response_model=RoleResponse)
async def create(
    create_data: RoleCreate,
    service: RoleService = Depends(get_role_service),
    _: User = Depends(require_permission("create:role"))
    ):
    return await service.create(create_data=create_data)

@router.post("/assignment")
async def assignment(
    create_data: RolePermission = Depends(),
    service: RoleService = Depends(get_role_service),
):
    return await service.assignment(create_data=create_data)

@router.get("", response_model=list[RoleResponse])
async def get_all(
    pagination: GetAll = Depends(),
    service: RoleService = Depends(get_role_service),
    _: User = Depends(require_permission("get_all:role"))
    ):
    return await service.get_all(pagination=pagination)


@router.get("/get/{id}", response_model=RoleResponse)
async def get_by_id(
    id: int,
    service: RoleService = Depends(get_role_service),
    _: User = Depends(require_permission("get:role"))
    ):
    return await service.get_by_id(id=id)


@router.put("/update/{id}", response_model=RoleResponse)
async def update(
    id: int, 
    update_data: RoleUpdate,
    service: RoleService = Depends(get_role_service),
    _: User = Depends(require_permission("update:role"))
    ):
    return await service.update(id=id, update_data=update_data)


@router.delete("/delete/{role_id}")
async def delete(
    id: int,
    service: RoleService = Depends(get_role_service),
    _: User = Depends(require_permission("delete:role"))
    ):
    await service.delete(id=id)
    return {"message": "Role deleted successfully"}
