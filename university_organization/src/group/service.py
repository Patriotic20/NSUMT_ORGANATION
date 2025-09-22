from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    GroupCreate,
    GroupUpdate,
    GroupGet
)

from core.utils.service import BasicService
from core.models.group import Group
from core.schemas.get_all import GetAll


class GroupService:
    def __init__(self , session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)
        
    async def create(self , create_data: GroupCreate):
        return await self.service.create(
            model=Group,
            create_data=create_data,
            filters=[Group.name == create_data.name]
            )
    
    async def get_all(self, pagination: GetAll):
        return await self.service.get(
            model=Group,
            pagination=pagination,
        )
    
    async def get_by_id(self, group_get: GroupGet):
        return await self.service.get(
            model=Group,
            filters=[
                Group.id == group_get.id,
                Group.faculty_id == group_get.faculty_id
                ],
            single=True
            )
    
    async def update(self, group_get: GroupGet, update_data: GroupUpdate):
        return await self.service.update(
            model=Group,
            filters=[
                Group.id == group_get.id,
                Group.faculty_id == group_get.faculty_id
                ],
            unique_filters=[Group.name == update_data.name],
            update_data=update_data
            )
        
    
    async def delete(self, group_get: GroupGet):
        await self.service.delete(
            model=Group,
            filters=[
                Group.id == group_get.id,
                Group.faculty_id == group_get.faculty_id
            ]
            )
        return {"message": "Group delete successfully"}

    

