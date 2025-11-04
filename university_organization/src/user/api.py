from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from .service import UserService
from .schemas import UserRoleCreate

from core.utils.database import db_helper
from core.models.user import User
from core.schemas.get_all import GetAll

from auth.utils.dependencies import require_permission




router = APIRouter(
    tags=["User"],
    prefix="/user"
)

def get_user_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return UserService(session=session)



@router.post("/assig_role_to_user")
async def assig(
    create_data: UserRoleCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.assig(user_role_create=create_data)


@router.get("")
async def get_all(
    pagination: Annotated[GetAll, Depends()],
    search: str | None = None,
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_permission("read:user")),
):
    return await service.get_all(pagination=pagination, search=search)

@router.get("/get/{id}")
async def get_by_id(
    id: int,
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_permission("read:user"))
):
    return await service.get_by_id(id=id)


@router.delete("/delete/{id}")
async def delete_user(
    id: int,
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_permission("delete:user"))
):
    await service.delete(id=id)
    return {"message": "User deleted successfully"}
