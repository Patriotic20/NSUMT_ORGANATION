from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models.faculty import Faculty
from core.models.group import Group
from core.models.student import Student
from sqlalchemy.orm import selectinload


class StatisticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def faculty_statistics(self, id: int):
        stmt = (
            select(Faculty)
            .where(Faculty.id == id)
            .options(
                selectinload(Faculty.groups).selectinload(Group.students)
            )
        ) 

        result = await self.session.execute(stmt)
        faculty = result.scalar_one_or_none()

        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty not found"
            )

        student_ids = []

        for group in faculty.groups:
            for student in group.students:
                student_ids.append(student.id)


    async def chair_statistics(self, id: int):
        pass
    
    async def teacher_statistics(self, id: int):
        pass