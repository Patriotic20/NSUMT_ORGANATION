from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.utils.database import db_helper
from .schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)
from .service import DepartmentService
from core.models.user import User
from core.schemas.get_all import GetAll
from auth.utils.dependencies import require_permission


router = APIRouter(
    tags=["Department"],
    prefix="/departments",
)

def get_department_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return DepartmentService(session=session)


@router.post("/create", response_model=DepartmentResponse)
async def create(
    create_data: DepartmentCreate,
    service: DepartmentService = Depends(get_department_service),
    _: User = Depends(require_permission("create:departments"))
):
    return await service.create(create_data=create_data)


@router.get("")
async def get_all(
    pagination: GetAll = Depends(),
    service: DepartmentService = Depends(get_department_service),
    _: User = Depends(require_permission("read:departments"))
):
    return await service.get_all(pagination=pagination)


@router.get("/get/{id}", response_model=DepartmentResponse)
async def get_by_id(
    id: int,
    service: DepartmentService = Depends(get_department_service),
    _: User = Depends(require_permission("read:departments"))
):
    return await service.get_by_id(id=id)


@router.put("/update/{id}", response_model=DepartmentResponse)
async def update(
    id: int,
    update_data: DepartmentUpdate,
    service: DepartmentService = Depends(get_department_service),
    _: User = Depends(require_permission("update:departments"))
):
    return await service.update(id=id, update_data=update_data)


@router.delete("/delete/{id}")
async def delete(
    id: int,
    service: DepartmentService = Depends(get_department_service),
    _: User = Depends(require_permission("delete:departments"))
):
    await service.delete(id=id)
    return {"message": "Department deleted successfully"}
