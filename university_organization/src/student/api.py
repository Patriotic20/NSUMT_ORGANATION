from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from .schemas import StudentResponse, StudentGet
from .service import StudentService


from core.utils.database import db_helper
from core.models.user import User
from core.schemas.get_all import GetAll
from auth.utils.dependencies import require_permission


router = APIRouter(
    tags=["Student"],
    prefix="/students",
)

def get_student_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return StudentService(session=session)


@router.get("")
async def get_all(
    pagination: GetAll = Depends(),
    service: StudentService = Depends(get_student_service),
    _: User = Depends(require_permission("read:students"))
    ):
    return await service.get_all(pagination=pagination)


@router.get("/get/{id}", response_model=StudentResponse)
async def get_by_id(
    student_get: StudentGet = Depends(),
    service: StudentService = Depends(get_student_service),
    _: User = Depends(require_permission("read:students"))
    ):
    return await service.get_by_id(student_get=student_get)


@router.delete("/delete/{id}", response_model=StudentResponse)
async def delete(
    student_get: StudentGet = Depends(),
    service: StudentService = Depends(get_student_service),
    _: User = Depends(require_permission("delete:students"))
):
    return await service.delete(student_get=student_get)


 
