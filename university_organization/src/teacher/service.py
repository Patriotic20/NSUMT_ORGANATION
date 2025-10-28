from sqlalchemy.ext.asyncio import AsyncSession

from core.utils.service import BasicService
from .schemas import (
    TeacherCreate,
    TeacherUpdate,
    TeacherGet    
)

from core.models.teacher import Teacher
from core.schemas.get_all import GetAll


class TeacherService:
    def __init__(self , session: AsyncSession):
        self.session = session
        self.service = BasicService(self.session)
        
    async def create(self , create_data: TeacherCreate):
       return await self.service.create(
            model=Teacher, 
            create_data=create_data,
            filters=[
                Teacher.user_id == create_data.user_id,
                Teacher.first_name == create_data.first_name,
                Teacher.last_name == create_data.last_name,
                Teacher.patronymic == create_data.patronymic
                ]
            )
        
        
    async def get_by_id(self , teacher_get: TeacherGet):
        return await self.service.get(
            model=Teacher,
            filters=[
                Teacher.id == teacher_get.id,
                Teacher.chair_id == teacher_get.chair_id,
                Teacher.user_id == teacher_get.user_id
                ],
            single=True
        )

    async def get_all(
        self,
        pagination: GetAll 
        ):
        return await self.service.get(
            model=Teacher,
            pagination=pagination
            )
    
    async def update(
        self, 
        teacher_get: TeacherGet,
        update_data: TeacherUpdate
        ):

        return await self.service.update(
            model=Teacher, 
            filters=[
                Teacher.id == teacher_get.id,
                Teacher.chair_id == teacher_get.chair_id,
                Teacher.user_id == teacher_get.user_id
            ],
            unique_filters=[
                Teacher.first_name == update_data.first_name,
                Teacher.last_name == update_data.last_name,
                Teacher.patronymic == update_data.patronymic
            ],
            update_data=update_data
            )
    
    async def delete(self, teacher_get: TeacherGet):
        await self.service.delete(
            model=Teacher, 
            filters=[
                Teacher.id == teacher_get.id,
                Teacher.chair_id == teacher_get.chair_id,
                Teacher.user_id == teacher_get.user_id
            ]
            )
        return {"message": "Teacher delete successfully"}

        

