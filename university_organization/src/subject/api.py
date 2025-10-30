from fastapi import APIRouter , Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import SubjectService
from .schemas import SubjectUpdate, SubjectBase, AssignTeacher


from core.utils.database import db_helper

from auth.schemas.auth import TokenPaylod
from auth.utils.dependencies import require_permission
from core.schemas.get_all import GetAll

router = APIRouter(
    tags=["Subject"],
    prefix="/subjects"
)

def get_subject_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return SubjectService(session=session)


@router.post("/create")
async def create(
    subject_data: SubjectBase,
    service: SubjectService = Depends(get_subject_service),
    _ : TokenPaylod = Depends(require_permission("create:subjects"))
):
    return await service.create_subject(subject_data=subject_data)

@router.post("/assign_teacher")
async def assign_teacher(
    assign_data: AssignTeacher = Depends(),
    service: SubjectService = Depends(get_subject_service),
    _ : TokenPaylod = Depends(require_permission("create:subjects"))

):
    return await service.assign_teacher(assign_data=assign_data)

@router.get("/get/{subject_id}")
async def get_by_id(
    subject_id: int,
    service: SubjectService = Depends(get_subject_service),
    _ : TokenPaylod = Depends(require_permission("read:subjects"))
):
    return await service.get_subject_by_id(subject_id=subject_id)


@router.get("")
async def get_all(
    pagination: GetAll = Depends(),
    service: SubjectService = Depends(get_subject_service),
    _ : TokenPaylod = Depends(require_permission("read:subjects"))
):
    return await service.get_all_subjects(pagination = pagination)

@router.put("/update/{subject_id}")
async def update(
    subject_id: int,
    subject_data: SubjectUpdate,
    service: SubjectService = Depends(get_subject_service),
    _ : TokenPaylod = Depends(require_permission("update:subjects"))
):
    return await service.update_subject(subject_id=subject_id, subject_data=subject_data)

@router.delete("/delete/{subject_id}")
async def delete(
    subject_id: int,
    service: SubjectService = Depends(get_subject_service),
    _ : TokenPaylod = Depends(require_permission("delete:subjects"))
):
    return await service.delete_subject(subject_id=subject_id)
