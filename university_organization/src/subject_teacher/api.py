from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import SubjectTeacherCreate
from .service import SubjectTeacherService
from .schemas import SubjectTeacherUpdate

from core.utils.database import db_helper

from auth.schemas.auth import TokenPaylod

from auth.utils.dependencies import require_permission

router = APIRouter(
    tags=["Subject Teacher"],
    prefix="/subject_teacher"
)

def get_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return SubjectTeacherService(session=session)

@router.post("/create")
async def create(
    create_data: SubjectTeacherCreate,
    service: SubjectTeacherService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("create:subject_teacher"))
):
    return await service.create(create_data=create_data)


@router.get("/get/{id}")
async def get_by_id(
    id: int,
    service: SubjectTeacherService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("read:subject_teacher"))
):
    return await service.get_by_id(id=id)


@router.get("/get/teacher/{id}")
async def get_by_teacher_id(
    id: int,
    service: SubjectTeacherService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("read:subject_teacher"))
):
    return await service.get_by_teacher_id(teacher_id=id)


@router.put("/update/{id}")
async def update(
    id: int,
    update_data: SubjectTeacherUpdate,
    service: SubjectTeacherService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("update:subject_teacher"))
):
    return await service.update(id = id, update_data = update_data)

@router.delete("/delete/{id}")
async def delete(
    id: int,
    service: SubjectTeacherService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("delete:subject_teacher"))
    
):
    return await service.delete(id=id)

