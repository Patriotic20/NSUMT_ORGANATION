from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    RoleCreate,
    RoleUpdate,
    RolePermission
)

from core.utils.service import BasicService
from core.models.role_permission_association import RolePermission
from core.schemas.get_all import GetAll
from core.models.role import Role


class RoleService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)
        
    async def create(self, create_data: RoleCreate):
        return await self.service.create(
            model=Role,
            create_data=create_data,
            filters=[
                Role.name == create_data.name
            ]
        )
    
    async def get_by_id(self, id: int):
        return await self.service.get(
            model=Role,
            filters=[
                Role.id == id
            ],
            single=True
            
        )
    
    async def get_all(
        self,
        pagination: GetAll
        ):
        return await self.service.get(
            model=Role,
            pagination=pagination
            )
    
    async def update(self, id: int, update_data: RoleUpdate):
        return await self.service.update(
            model=Role,
            filters=[
                Role.id == id
            ],
            unique_filters=[
                Role.name == update_data.name
            ],
            update_data=update_data
            )
    
    async def delete(self, id: int):
        return await self.service.delete(
            model=Role,
            filters=[
                Role.id == id
            ]
            )
    
    async def assignment(self, create_data: RolePermission):
        return await self.service.create(
            model=RolePermission,
            create_data=create_data,
            )
        
    