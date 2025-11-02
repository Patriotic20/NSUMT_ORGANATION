from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from sqlalchemy.orm import selectinload


from sqlalchemy import select

from core.models.subject_teacher_association import SubjectTeacher
from core.utils.service import BasicService

from .schemas import SubjectTeacherCreate


class SubjectTeacherService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)
    
    async def create(self, create_data: SubjectTeacherCreate):
        return await self.service.create(
            create_data=create_data,
            model=SubjectTeacher,
            filters=[
                SubjectTeacher.subject_id == create_data.subject_id, 
                SubjectTeacher.teacher_id == create_data.teacher_id
                ]
        )
    
    async def get_by_id(self, id: int):
        stmt = (
            select(SubjectTeacher)
            .where(SubjectTeacher.id == id)
            .options(
                selectinload(SubjectTeacher.subject),
                selectinload(SubjectTeacher.teacher)
            )
        )

        result = await self.session.execute(stmt)
        subject_teacher = result.scalar_one_or_none()  

        if not subject_teacher:
            raise HTTPException(status_code=404, detail="SubjectTeacher not found")

        return subject_teacher
    
    async def get_by_teacher_id(self, teacher_id: int):
        
        stmt = (
            select(SubjectTeacher)
            .where(SubjectTeacher.teacher_id == teacher_id)
            .options(
                selectinload(SubjectTeacher.subject)
            )
        )
        
        
        result = await self.session.execute(stmt)
        subject_teacher = result.scalar_one_or_none() 
        
        if not subject_teacher:
            raise HTTPException(status_code=404, detail="SubjectTeacher not found")
        
        subjects = [gt.subject for gt in subject_teacher if gt.subject is not None]
        return subjects
        
        
