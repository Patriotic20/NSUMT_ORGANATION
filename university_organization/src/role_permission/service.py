from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from fastapi import HTTPException

from core.models.role_permission_association import RolePermission


class RolePermissionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    
    async def create(self):
        pass
    
    
    async def get_by_id(self, id: int):
        
        stmt = (
            select(RolePermission)
            .where(RolePermission.id == id)
            .options(
                selectinload(RolePermission.role),
                selectinload(RolePermission.permission)
            )
            )
        
        result = await self.session.execute(stmt)
        data = result.scalars().first()
        
        if not data:
            raise HTTPException()
        pass
    
    async def get_all(self):
        pass
    
    async def update(self):
        pass
    
    async def delete(self):
        pass
