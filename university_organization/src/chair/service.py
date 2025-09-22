from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import ChairCreate, ChairUpdate, ChairGet

from core.utils.service import BasicService
from core.models.chair import Chair
from core.schemas.get_all import GetAll


class ChairService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)

    async def create(self, create_data: ChairCreate):
        return await self.service.create(
            model=Chair, 
            create_data=create_data, 
            filters=[Chair.name == create_data.name]
            )

    async def get_by_id(self, chair_get: ChairGet):
        return await self.service.get(
            model=Chair,
            filters=[Chair.id == chair_get.id, Chair.faculty_id == chair_get.faculty_id],
            single=True
        )

    async def get_all(self, pagination: GetAll):
        return await self.service.get(
            model=Chair, 
            pagination=pagination
            )

    async def update(
        self, 
        chair_get: ChairGet,
        update_data: ChairUpdate
        ):
        return await self.service.update(
            model=Chair,
            update_data=update_data,
            filters=[Chair.id == chair_get.id, Chair.faculty_id == chair_get.faculty_id],
            unique_filters=[Chair.name == update_data.name],
        )

    async def delete(self, chair_get: ChairGet):
        await self.service.delete(
            model=Chair, 
            filters=[
                Chair.id == chair_get.id, 
                Chair.faculty_id == chair_get.faculty_id
                ])
        return {"message": "Delete successfully"}
        


