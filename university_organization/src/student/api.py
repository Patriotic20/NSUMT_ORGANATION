from fastapi import APIRouter, Depends, Query, Path
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
    search: str | None = Query(
        None,
        description="Qidiruv uchun matn (familiya, ism, otasining ismi yoki user_ID raqami bo‘yicha)"
    ),
    pagination: GetAll = Depends(),
    service: StudentService = Depends(get_student_service),
    _: User = Depends(require_permission("read:students"))
    ):
    return await service.get_all(pagination=pagination, search=search)


@router.get("/get/{id}", response_model=StudentResponse)
async def get_by_id(
    id: int = Path(..., description="Talabaning yagona ID raqami"),
    service: StudentService = Depends(get_student_service),
    _: User = Depends(require_permission("read:students"))
    ):
    return await service.get_by_id(student_get=id)


@router.delete("/delete/{id}", response_model=StudentResponse)
async def delete(
    student_get: StudentGet = Depends(),
    service: StudentService = Depends(get_student_service),
    _: User = Depends(require_permission("delete:students"))
):
    return await service.delete(student_get=student_get)


 
