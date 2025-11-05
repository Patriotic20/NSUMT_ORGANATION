from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import UserRoleService
from .schemas import UserRoleCreate, UserRoleUpdate
from core.utils.database import db_helper
from auth.schemas.auth import TokenPaylod
from auth.utils.dependencies import require_permission


router = APIRouter(
    prefix="/user_role",
    tags=["User Role"],
)


def get_service(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> UserRoleService:
    """Dependency to provide UserRoleService."""
    return UserRoleService(session=session)


@router.post("/create")
async def create_user_role(
    create_data: UserRoleCreate,
    service: UserRoleService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("create:user_role")),
):
    """Create a new UserRole."""
    return await service.create(create_data=create_data)


@router.get("/get/{id}")
async def get_user_role_by_id(
    id: int,
    service: UserRoleService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("read:user_role")),
):
    """Retrieve a UserRole by its ID."""
    return await service.get_by_id(id=id)


@router.get("")
async def get_roles_for_user(
    user_id: int,
    service: UserRoleService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("read:user_role")),
):
    """Retrieve all roles assigned to a specific user."""
    return await service.get_by_user_id(user_id=user_id)


@router.put("/update/{id}")
async def update_user_role(
    id: int,
    update_data: UserRoleUpdate,
    service: UserRoleService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("update:user_role")),
):
    """Update an existing UserRole by ID."""
    return await service.update(id=id, update_data=update_data)


@router.delete("/delete/{id}")
async def delete_user_role(
    id: int,
    service: UserRoleService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("delete:user_role")),
):
    """Delete a UserRole by ID."""
    return await service.delete(id=id)
