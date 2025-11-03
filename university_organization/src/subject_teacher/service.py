from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from sqlalchemy.orm import selectinload


from sqlalchemy import select

from core.models.subject_teacher_association import SubjectTeacher
from core.utils.service import BasicService
from core.models.teacher import Teacher
from .schemas import SubjectTeacherCreate
from .schemas import SubjectTeacherUpdate

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
    
    async def get_by_teacher_id(self, user_id: int):
        stmt = (
            select(Teacher)
            .where(Teacher.user_id == user_id)
            .options(
                selectinload(Teacher.subject_teachers).selectinload(SubjectTeacher.subject)
            )
        )

        result = await self.session.execute(stmt)
        teacher = result.scalar_one_or_none()

        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")

        subjects = [st.subject for st in teacher.subject_teachers if st.subject is not None]

        if not subjects:
            raise HTTPException(status_code=404, detail="No subjects found for this teacher")

        return subjects
        
    async def update(self, id: int, update_data: SubjectTeacherUpdate):
        return await self.service.update(
            model = SubjectTeacher,
            filters = [SubjectTeacher.id == id],
            unique_filters = [
                SubjectTeacher.subject_id == update_data.subject_id,
                SubjectTeacher.teacher_id == update_data.teacher_id
                ],
            update_data=update_data
        )
        
    async def delete(self, id: int):
        return await self.service.delete(
            model=SubjectTeacher,
            filters=[SubjectTeacher.id == id]
        )
