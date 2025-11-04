from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from fastapi import HTTPException, status


from core.utils.service import BasicService
from core.models import User
from core.models import UserRole
from core.schemas.get_all import GetAll

from .schemas import (
    UserResponse, 
    WorkerResponse, 
    StudentResponse, 
    TeacherResponse,
    UserRoleCreate
)

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)

    async def get_by_id(self, id: int) -> UserResponse:
        stmt = (
            select(User)
            .options(
                selectinload(User.roles),
                selectinload(User.worker),
                selectinload(User.student),
                selectinload(User.teacher),
            )
            .where(User.id == id)
        )
        result = await self.session.execute(stmt)
        user_data = result.scalars().first()

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse(
            id=user_data.id,
            username=user_data.username,
            roles=[role.name for role in user_data.roles],
            worker=WorkerResponse(
                id=user_data.worker.id,
                department_id=user_data.worker.department_id,
                first_name=user_data.worker.first_name,
                last_name=user_data.worker.last_name,
                patronymic=user_data.worker.patronymic,
            ) if user_data.worker else None,
            student=StudentResponse(
                id=user_data.student.id,
                department_id=user_data.student.department_id,
                first_name=user_data.student.first_name,
                last_name=user_data.student.last_name,
                patronymic=user_data.student.patronymic,
            ) if user_data.student else None,
            teacher=TeacherResponse(
                id=user_data.teacher.id,
                department_id=user_data.teacher.department_id,
                first_name=user_data.teacher.first_name,
                last_name=user_data.teacher.last_name,
                patronymic=user_data.teacher.patronymic,
            ) if user_data.teacher else None,
        )

    async def get_all(
        self,
        pagination: GetAll,
        search: str | None = None,
    ):
        return await self.service.get(
            model=User, 
            pagination=pagination,
            search=search,
            search_fields=["username"]
            )

    async def delete(self, id: int):
        await self.service.delete(model=User, filters=[User.id == id])
        return {"message": "User delete successfully"}

    
    async def assig(self, user_role_create: UserRoleCreate):
        return await self.service.create(model=UserRole, create_data=user_role_create)
