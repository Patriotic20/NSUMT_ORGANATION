from sqlalchemy.ext.asyncio import AsyncSession

from core.utils.service import BasicService
from core.models.subject import Subject
from core.models.subject_teacher_association import SubjectTeacher
from core.schemas.get_all import GetAll

from .schemas import SubjectUpdate, SubjectBase , AssignTeacher

class SubjectService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)

    async def create_subject(self, subject_data: SubjectBase):
        return await self.service.create(
            model=Subject,
            create_data=subject_data,
            filters=[Subject.name == subject_data.name]
            )
        
        
    async def assign_teacher(self, assign_data: AssignTeacher):
        return await self.service.create(
            model = SubjectTeacher,
            filters = [
                SubjectTeacher.subject_id == assign_data.subject_id,
                SubjectTeacher.teacher_id == assign_data.teacher_id,
                ],
            create_data = assign_data,
        )
        

    async def get_subject_by_id(self, subject_id: int | None = None):
        return await self.service.get(
            model=Subject,
            filters=[Subject.id == subject_id],
            single=True
        )

    async def get_all_subjects(
        self, 
        pagination: GetAll, 
        search: str | None = None
        ):
        return await self.service.get(
            model=Subject,
            pagination = pagination,
            search=search,
            search_fields=["name"]
        )


    async def update_subject(self, subject_data: SubjectUpdate, subject_id: int):
        return await self.service.update(
            model = Subject,
            filters=[Subject.id == subject_id],
            unique_filters=[Subject.name == subject_data.name],
            update_data=subject_data,
        )

    async def delete_subject(self, subject_id: int):
        return await self.service.delete(
            model=Subject,
            filters=[Subject.id == subject_id]
        )

        
        
