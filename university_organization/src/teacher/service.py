from sqlalchemy.ext.asyncio import AsyncSession

from core.utils.service import BasicService
from sqlalchemy import select

from .schemas import (
    TeacherBase,
    TeacherUpdate,
    TeacherGet,
    CreateTeacherRole    
)

from core.models.teacher import Teacher
from core.schemas.get_all import GetAll
from core.models.role import Role
from core.models.user_role_association import UserRole


class TeacherService:
    def __init__(self , session: AsyncSession):
        self.session = session
        self.service = BasicService(self.session)
        
    async def create(self, create_data: TeacherBase):
        # Try to create or get existing Teacher
        teacher = await self.service.create(
            model=Teacher,
            create_data=create_data,
            filters=[Teacher.user_id == create_data.user_id]
        )

        # If created (or found), ensure the "teacher" role exists
        if teacher:
            await self.create_check(user_id=create_data.user_id)

        return teacher
        
        
    async def get_by_id(self , teacher_get: TeacherGet):
        return await self.service.get(
            model=Teacher,
            filters=[Teacher.id == teacher_get.teacher_id],
            single=True
        )

    async def get_all(
        self,
        pagination: GetAll, 
        search: str | None = None,
        ):
        return await self.service.get(
            model=Teacher,
            pagination=pagination,
            search=search,
            search_fields=["first_name", "last_name", "patronymic"]
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

        
    async def create_check(self, user_id: int):
        # Check if the "teacher" role exists
        existing = await self.session.scalar(
            select(Role).where(Role.name == "teacher")
        )

        # If not, create it
        if not existing:
            new_role = Role(name="teacher")
            self.session.add(new_role)
            await self.session.commit()
            await self.session.refresh(new_role)
            existing = new_role

        # Always try to create UserRole (even if duplicate might exist)
        user_role_data = CreateTeacherRole(role_id=existing.id, user_id=user_id)
        await self.service.create(
            model=UserRole,
            filters=[
                UserRole.role_id == user_role_data.role_id, 
                UserRole.user_id == user_role_data.user_id
                ],
            create_data=user_role_data
        )
