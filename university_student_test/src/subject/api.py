from fastapi import APIRouter , Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import SubjectService
from .schemas import SubjectUpdate, SubjectCreate

from core.database.db_helper import db_helper

from auth.schemas.auth import TokenPaylod
from auth.utils.security import require_permission

router = APIRouter(
    tags=["Subject"],
    prefix="/subjects"
)

def get_subject_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return SubjectService(session=session)


@router.post("/create")
async def create(
    subject_data: SubjectCreate,
    service: SubjectService = Depends(get_subject_service),
    current_user: TokenPaylod = Depends(require_permission("create:subjects"))
):
    return await service.create_subject(subject_data=subject_data, teacher_id=current_user.user_id)

@router.get("/get/{subject_id}")
async def get_by_id(
    subject_id: int,
    service: SubjectService = Depends(get_subject_service),
    current_user: TokenPaylod = Depends(require_permission("read:subjects"))
):
    return await service.get_subject_by_id(subject_id=subject_id, teacher_id=current_user.user_id)


@router.get("")
async def get_all(
    limit: int = 20, 
    offset: int = 0,
    service: SubjectService = Depends(get_subject_service),
    current_user: TokenPaylod = Depends(require_permission("read:subjects"))
):
    return await service.get_all_subjects(limit=limit , offset=offset, teacher_id=current_user.user_id)

@router.put("/update/{subject_id}")
async def update(
    subject_id: int,
    subject_data: SubjectUpdate,
    service: SubjectService = Depends(get_subject_service),
    current_user: TokenPaylod = Depends(require_permission("update:subjects"))
):
    return await service.update_subject(subject_id=subject_id, teacher_id=current_user.user_id, subject_data=subject_data)

@router.delete("/delete/{subject_id}")
async def delete(
    subject_id: int,
    service: SubjectService = Depends(get_subject_service),
    current_user: TokenPaylod = Depends(require_permission("delete:subjects"))
):
    return await service.delete_subject(subject_id=subject_id, teacher_id=current_user.user_id)
