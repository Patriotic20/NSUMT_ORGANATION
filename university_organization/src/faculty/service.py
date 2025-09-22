from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import FacultyCreate, FacultyUpdate

from core.utils.service import BasicService
from core.models.faculty import Faculty
from core.schemas.get_all import GetAll


class FacultyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)

    async def create(self, create_data: FacultyCreate):
        return await self.service.create(
            model=Faculty, 
            create_data=create_data, 
            filters=[Faculty.name == create_data.name]
            )

    async def get_by_id(self, id: int):
        return await self.service.get(
            model=Faculty,
            filters=[Faculty.id == id],
            single=True
        ) 

    async def get_all(self, pagination: GetAll):
        return await self.service.get(
            model=Faculty, 
            pagination=pagination
            )

    async def update(self, id: int, update_data: FacultyUpdate):
        return await self.service.update(
            model=Faculty,
            filters=[Faculty.id == id],
            unique_filters=[Faculty.name == update_data.name],
            update_data=update_data.model_dump(exclude_unset=True),
        )

    async def delete(self, id: int):
        await self.service.delete(
            model=Faculty, 
            filters=[Faculty.id == id]
            )
        return {"message": "Delete successfully"}


