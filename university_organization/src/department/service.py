from sqlalchemy.ext.asyncio import AsyncSession

from core.utils.service import BasicService
from .schemas import DepartmentCreate, DepartmentUpdate
from core.models.department import Department
from core.schemas.get_all import GetAll


class DepartmentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)

    async def create(self, create_data: DepartmentCreate):
        return await self.service.create(
            model=Department,
            create_data=create_data,
            filters=[Department.name == create_data.name],
        )

    async def get_by_id(self, id: int):
        return await self.service.get(
            model=Department,
            filters=[Department.id == id],
            single=True,
        )

    async def get_all(self, pagination: GetAll):
        return await self.service.get(
            model=Department,
            pagination=pagination,
        )

    async def update(self, id: int, update_data: DepartmentUpdate):
        return await self.service.update(
            model=Department,
            filters=[Department.id == id],
            unique_filters=[Department.name == update_data.name],
            update_data=update_data.model_dump(exclude_unset=True),
        )

    async def delete(self, id: int):
        await self.service.delete(
            model=Department,
            filters=[Department.id == id],
        )
        return {"message": "Delete successfully"}
