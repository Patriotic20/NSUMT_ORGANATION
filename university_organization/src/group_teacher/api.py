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

@router.post()
async def create(
    create_data: GroupTeacherCreate,
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
    

# @router.get()
# async def get_all(
#     pagination: GetAll = Depends()
# ):
#     pass

# @router.put("/update")
# async def update(
#     update_data: GroupTeacherUpdate = Depends()
# ):
#     pass

# @router.delete("/delete/{id}")
# async def delete(
#     id: int,
#     group_id: int | None = None,
#     teacher_id: int | None = None,
# ):
#     pass

