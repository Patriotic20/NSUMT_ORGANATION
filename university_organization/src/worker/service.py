from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import WorkerCreate, WorkerUpdate , WorkerGet 
from core.utils.service import BasicService
from core.models.worker import Worker
from core.schemas.get_all import GetAll


class WorkerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)

    async def create(self, create_data: WorkerCreate):
        return await self.service.create(
            model=Worker,
            create_data=create_data,
            filters=[
                Worker.first_name == create_data.first_name,
                Worker.last_name == create_data.last_name,
                Worker.patronymic == create_data.patronymic,
            ],
        )

    async def get_by_id(self, worker_get: WorkerGet):
        return await self.service.get(
            model=Worker,
            filters=[
                Worker.id == worker_get.id, 
                Worker.user_id == worker_get.user_id, 
                Worker.department_id == worker_get.department_id
                ],
            single=True,
        )

    async def get_all(self, pagination: GetAll):
        return await self.service.get(
            model=Worker,
            pagination=pagination,
        )

    async def update(self, worker_get: WorkerGet, update_data: WorkerUpdate):
        return await self.service.update(
            model=Worker,
            filters=[
                Worker.id == worker_get.id, 
                Worker.user_id == worker_get.user_id, 
                Worker.department_id == worker_get.department_id
                ],

            unique_filters=[
                Worker.first_name == update_data.first_name,
                Worker.last_name == update_data.last_name,
                Worker.patronymic == update_data.patronymic,
            ],
            update_data=update_data.model_dump(exclude_unset=True),
        )

    async def delete(self, worker_get: WorkerGet):
        await self.service.delete(
            model=Worker,
            filters=[
                Worker.id == worker_get.id, 
                Worker.user_id == worker_get.user_id, 
                Worker.department_id == worker_get.department_id
                ],
        )
        return {"message": "Delete successfully"}
