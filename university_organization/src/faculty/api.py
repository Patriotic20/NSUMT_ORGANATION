from fastapi import APIRouter , Depends
from sqlalchemy.ext.asyncio import AsyncSession


from .service import FacultyService
from .schemas import (
    FacultyCreate,
    FacultyUpdate,
    FacultyResponse,
)

from core.utils.database import db_helper
from core.models.user import User
from core.schemas.get_all import GetAll
from auth.utils.dependencies import require_permission


router = APIRouter(
    tags=["Faculty"],
    prefix="/faculties",
)

def get_faculty_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return FacultyService(session=session)

@router.post("/create", response_model=FacultyResponse)
async def create(
    create_data: FacultyCreate,
    service: FacultyService = Depends(get_faculty_service),
    _: User = Depends(require_permission("create:faculties"))
    ):
    return await service.create(create_data=create_data)

@router.get("")
async def get_all(
    pagination: GetAll = Depends(),
    service: FacultyService = Depends(get_faculty_service),
    _: User = Depends(require_permission("read:faculties"))
    ):
    return await service.get_all(pagination=pagination)

@router.get("/get/{id}", response_model=FacultyResponse)
async def get_by_id(
    id: int,
    service: FacultyService = Depends(get_faculty_service),
    _: User = Depends(require_permission("read:faculties"))
    ):
    return await service.get_by_id(id=id)

@router.put("/update/{id}")
async def update(
    id: int, 
    update_data: FacultyUpdate,
    service: FacultyService = Depends(get_faculty_service),
    _: User = Depends(require_permission("update:faculties"))
    ):
    return await service.update(id=id, update_data=update_data)

@router.delete("/delete/{id}")
async def delete(
    id: int,
    service: FacultyService = Depends(get_faculty_service),
    _: User = Depends(require_permission("delete:faculties"))
    ):
    await service.delete(id=id)
    return {"message": "Faculty deleted successfully"}
