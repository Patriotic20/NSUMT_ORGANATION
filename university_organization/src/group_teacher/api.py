from fastapi import APIRouter, Depends
from core.schemas.get_all import GetAll

from .schemas import GroupTeacherCreate
from .schemas import GroupTeacherUpdate

from sqlalchemy.ext.asyncio import AsyncSession
from core.utils.database import db_helper
from .service import GroupTeacherService

from auth.utils.dependencies import require_permission

from auth.schemas.auth import TokenPaylod

router = APIRouter(
    tags=["Group Teacher"],
    prefix="/group_teacher"
)


def get_group_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return GroupTeacherService(session=session)

@router.post("/create")
async def create(
    create_data: GroupTeacherCreate = Depends(),
    service: GroupTeacherService = Depends(get_group_service),
    _: TokenPaylod = Depends(require_permission("create:group_teacher"))
):
    return await service.create(create_data=create_data)


@router.get("/get/{id}")
async def get_by_id(
    id: int,
    service: GroupTeacherService = Depends(get_group_service),
    _: TokenPaylod = Depends(require_permission("read:group_teacher"))
):
    return await service.get_by_id(id=id)


@router.get("/get/teacher/{user_id}")
async def get_by_teacher_id(
    user_id: int,
    service: GroupTeacherService = Depends(get_group_service),
    _: TokenPaylod = Depends(require_permission("read:group_teacher"))
):
    return await service.get_by_teacher_id(user_id=user_id)
    

@router.put("/update/{id}")
async def update(
    id: int,
    update_data: GroupTeacherUpdate = Depends(),
    service: GroupTeacherService = Depends(get_group_service),
    _: TokenPaylod = Depends(require_permission("update:group_teacher"))
):
    return await service.update(id=id, update_data=update_data)

@router.delete("/delete/{id}")
async def delete(
    id: int,
    service: GroupTeacherService = Depends(get_group_service),
    _: TokenPaylod = Depends(require_permission("delete:group_teacher"))
):
    return await service.delete(id=id)

