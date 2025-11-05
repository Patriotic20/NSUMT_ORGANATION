from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from fastapi import HTTPException, status

from .schemas import RolePermissionCreate, RolePermissionUpdate
from core.models.role_permission_association import RolePermission
from core.models.role import Role
from core.utils.service import BasicService


class RolePermissionService:
    """Service class for managing RolePermission operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)

    async def create(self, create_data: RolePermissionCreate):
        """Create a new RolePermission if it does not already exist."""
        return await self.service.create(
            model=RolePermission,
            filters=[
                RolePermission.role_id == create_data.role_id,
                RolePermission.permission_id == create_data.permission_id,
            ],
            create_data=create_data,
        )

    async def get_by_id(self, id: int):
        """Retrieve a RolePermission by its ID."""
        stmt = (
            select(RolePermission)
            .where(RolePermission.id == id)
            .options(
                selectinload(RolePermission.role),
                selectinload(RolePermission.permission),
            )
        )
        result = await self.session.execute(stmt)
        data = result.scalars().first()

        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RolePermission with id {id} not found",
            )

        return data

    async def get_permissions_for_role(self, role_id: int):
        """Retrieve all permissions assigned to a specific role."""
        stmt = (
            select(Role)
            .where(Role.id == role_id)
            .options(
                selectinload(Role.role_permissions).selectinload(
                    RolePermission.permission
                )
            )
        )
        result = await self.session.execute(stmt)
        role = result.scalars().first()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with id {role_id} not found",
            )

        permissions = [
            rp.permission.name
            for rp in role.role_permissions
            if rp.permission is not None
        ]

        return {
            "role_id": role.id,
            "role_name": role.name,
            "permissions": permissions,
        }

    async def update(self, id: int, update_data: RolePermissionUpdate):
        """Update an existing RolePermission by ID."""
        return await self.service.update(
            model=RolePermission,
            filters=[RolePermission.id == id],
            unique_filters=[
                RolePermission.role_id == update_data.role_id,
                RolePermission.permission_id == update_data.permission_id,
            ],
            update_data=update_data,
        )

    async def delete(self, id: int):
        """Delete a RolePermission by ID."""
        return await self.service.delete(
            model=RolePermission,
            filters=[RolePermission.id == id],
        )
