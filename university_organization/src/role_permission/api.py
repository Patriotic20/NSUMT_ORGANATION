from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import RolePermissionService
from .schemas import RolePermissionCreate, RolePermissionUpdate
from core.utils.database import db_helper
from auth.schemas.auth import TokenPaylod
from auth.utils.dependencies import require_permission


router = APIRouter(
    prefix="/role_permission",
    tags=["Role Permission"],
)


def get_service(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> RolePermissionService:
    """Dependency to provide RolePermissionService."""
    return RolePermissionService(session=session)


@router.post("/create")
async def create_role_permission(
    create_data: RolePermissionCreate,
    service: RolePermissionService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("create:role_permission")),
):
    """Create a new RolePermission."""
    return await service.create(create_data=create_data)


@router.get("/get/{id}")
async def get_role_permission_by_id(
    id: int,
    service: RolePermissionService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("read:role_permission")),
):
    """Retrieve a RolePermission by its ID."""
    return await service.get_by_id(id=id)


@router.get("")
async def get_permissions_for_role(
    role_id: int,
    service: RolePermissionService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("read:role_permission")),
):
    """Retrieve all permissions assigned to a specific role."""
    return await service.get_permissions_for_role(role_id=role_id)


@router.put("/update/{id}")
async def update_role_permission(
    id: int,
    update_data: RolePermissionUpdate,
    service: RolePermissionService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("update:role_permission")),
):
    """Update an existing RolePermission by ID."""
    return await service.update(id=id, update_data=update_data)


@router.delete("/delete/{id}")
async def delete_role_permission(
    id: int,
    service: RolePermissionService = Depends(get_service),
    _: TokenPaylod = Depends(require_permission("delete:role_permission")),
):
    """Delete a RolePermission by ID."""
    return await service.delete(id=id)
