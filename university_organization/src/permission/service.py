from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .schemas import PermissionCreate, PermissionUpdate

from core.utils.service import BasicService
from core.models.permission import Permission
from core.schemas.get_all import GetAll


class PermissionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)
    
    async def create(self, create_data: PermissionCreate):
        return await self.service.create(
            model=Permission,
            create_data=create_data,
            filters=[Permission.name == create_data.name]
        )
        
    async def get_by_id(self, id: int):
        return await self.service.get(
             model=Permission, 
             single=True,
             filters=[Permission.id == id]
        )
    
    async def get_all(self, pagination: GetAll):
        return await self.service.get(
            model=Permission,
            pagination=pagination
        )
    
    async def update(self, id: int, update_data: PermissionUpdate):
        return await self.service.update(
            model=Permission,
            filters=[Permission.id == id],
            unique_filters=[Permission.name == update_data.name],
            update_data=update_data
        )
    
    async def delete(self, id: int):
        return await self.service.delete(
            model=Permission,
            filters=[Permission.id == id]
        )
        
        
    async def sync_permissions(self, perms: list[PermissionCreate]):
        
        existing = {
            p.name for p in (await self.session.execute(select(Permission))).scalars().all()
        }

        
        new_perms = [
            Permission(name=p.name)
            for p in perms
            if p.name not in existing
        ]

        if new_perms:
            self.session.add_all(new_perms)
            await self.session.commit()

        return {
            "added": [p.name for p in new_perms],
            "skipped": list(existing),
        }
