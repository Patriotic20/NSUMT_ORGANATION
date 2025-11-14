from sqlalchemy.ext.asyncio import AsyncSession


from .schemas import StudentGet

from core.utils.service import BasicService
from core.models.student import Student
from core.schemas.get_all import GetAll


class StudentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)
        
    async def get_by_id(self, id: int):
        return await self.service.get(
            model=Student,
            filters=[Student.id == id],
            single=True
        )
    
    async def get_all(
            self,
            pagination: GetAll,
            search: str | None = None
        ):
        return await self.service.get(
            model=Student,
            search=search,
            search_fields=[
                "user_id",
                "last_name", 
                "third_name", 
                "first_name", 
                "student_id_number"
            ],
            pagination=pagination
        )

        
        
    async def delete(self, student_get: StudentGet):
        return await self.service.delete(
            model=Student,
            filters=[
                Student.id == student_get.id,
            ]
        )

    
