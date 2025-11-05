from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from fastapi import HTTPException, status

from .schemas import UserRoleCreate, UserRoleUpdate
from core.utils.service import BasicService
from core.models.user_role_association import UserRole
from core.models.user import User


class UserRoleService:
    """Service class for managing UserRole operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)

    async def create(self, create_data: UserRoleCreate):
        """Create a new UserRole if it does not already exist."""
        return await self.service.create(
            model=UserRole,
            filters=[
                UserRole.user_id == create_data.user_id,
                UserRole.role_id == create_data.role_id,
            ],
            create_data=create_data,
        )

    async def get_by_id(self, id: int):
        """Retrieve a UserRole by its ID."""
        stmt = (
            select(UserRole)
            .where(UserRole.id == id)
            .options(
                selectinload(UserRole.user),
                selectinload(UserRole.role),
            )
        )
        result = await self.session.execute(stmt)
        data = result.scalars().first()

        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"UserRole with id {id} not found",
            )

        return data

    async def get_by_user_id(self, user_id: int):
        """Retrieve all roles assigned to a specific user."""
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.user_roles).selectinload(
                    UserRole.role
                )
            )
        )
        result = await self.session.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )

        roles = [
            ur.role.name
            for ur in user.user_roles
            if ur.role is not None
        ]

        return {
            "user_id": user.id,
            "user_name": user.username if hasattr(user, "username") else None,
            "roles": roles,
        }

    async def update(self, id: int, update_data: UserRoleUpdate):
        """Update an existing UserRole by ID."""
        return await self.service.update(
            model=UserRole,
            filters=[UserRole.id == id],
            unique_filters=[
                UserRole.user_id == update_data.user_id,
                UserRole.role_id == update_data.role_id,
            ],
            update_data=update_data,
        )

    async def delete(self, id: int):
        """Delete a UserRole by ID."""
        return await self.service.delete(
            model=UserRole,
            filters=[UserRole.id == id],
        )
