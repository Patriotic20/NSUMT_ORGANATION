from fastapi import APIRouter , Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import TeacherService
from .schemas import (
    TeacherBase,
    TeacherUpdate,
    TeacherResponse,
    TeacherGet
)

from core.utils.database import db_helper
from core.models.user import User
from core.schemas.get_all import GetAll
from auth.utils.dependencies import require_permission
from auth.schemas.auth import TokenPaylod

router = APIRouter(
    tags=["Teacher"],
    prefix="/teachers",
)

def get_teacher_service(session : AsyncSession = Depends(db_helper.session_getter)):
    return TeacherService(session=session)

@router.post("/create", response_model=TeacherResponse)
async def create(
    teacher_data: TeacherBase,
    service: TeacherService = Depends(get_teacher_service),
    _ : TokenPaylod = Depends(require_permission("create:teachers"))
):
    return await service.create(create_data=teacher_data)
    


@router.get("")
async def get_all(
    search: str | None = None,
    pagination: GetAll = Depends(),
    service: TeacherService = Depends(get_teacher_service),
    _: User = Depends(require_permission("read:teachers"))
    ):
    return await service.get_all(pagination=pagination, search=search)
    


@router.get("/get/{id}", response_model=TeacherResponse)
async def get_by_id(
    teacher_get: TeacherGet = Depends(),
    service: TeacherService = Depends(get_teacher_service),
    _: User = Depends(require_permission("read:teachers"))
    ):
    return await service.get_by_id(teacher_get=teacher_get)
    


@router.put("/update/{id}", response_model=TeacherResponse)
async def update(
    teacher_data: TeacherUpdate,
    teacher_get: TeacherGet = Depends(),
    service: TeacherService = Depends(get_teacher_service),
    _: User = Depends(require_permission("update:teachers"))
    ):
    return await service.update(teacher_get=teacher_get, update_data=teacher_data)


@router.delete("/delete/{id}")
async def delete(
    teacher_get: TeacherGet = Depends(),
    service: TeacherService = Depends(get_teacher_service),
    _: User = Depends(require_permission("delete:teachers"))
    ):
    await service.delete(teacher_get=teacher_get)
    return {"message": "Teacher deleted successfully"}
