from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from core.utils.basic_service import BasicService
from core.models.subjects import Subject
from .schemas import SubjectCreate, SubjectUpdate, SubjectBase


class SubjectService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(db=self.session)

    async def create_subject(self, subject_data: SubjectBase, teacher_id: int):
        subject_data = SubjectCreate(name=subject_data.name, teacher_id=teacher_id)
        return await self.service.create(model=Subject, obj_items=subject_data)

    async def get_subject_by_id(self, subject_id: int | None = None, teacher_id: int | None = None):
        filters = self._build_subject_filter(subject_id=subject_id, teacher_id=teacher_id)
        result = await self.service.get(model=Subject, limit=1, filters=filters)
        subject = result[0] if result else None

        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with id {subject_id} not found"
            )
        return subject

    async def get_all_subjects(self, limit: int = 20, offset: int = 0, teacher_id: int | None = None):
        filters = self._build_subject_filter(teacher_id=teacher_id)
        return await self.service.get(model=Subject, limit=limit, offset=offset, filters=filters)

    async def update_subject(self, subject_data: SubjectUpdate, subject_id: int, teacher_id: int | None = None):
        filters = self._build_subject_filter(subject_id=subject_id, teacher_id=teacher_id)
        return await self.service.update(model=Subject, filters=filters, update_data=subject_data)

    async def delete_subject(self, subject_id: int, teacher_id: int | None = None):
        filters = self._build_subject_filter(subject_id=subject_id, teacher_id=teacher_id)
        await self.service.delete(model=Subject, filters=filters)
        return {"message": "Successfully deleted subject"}

    @staticmethod
    def _build_subject_filter(subject_id: int | None = None, teacher_id: int | None = None):
        # Require at least one argument
        if subject_id is None and teacher_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You need to provide subject_id or teacher_id"
            )

        filters = []
        if subject_id is not None:
            filters.append(Subject.id == subject_id)
        if teacher_id is not None:
            filters.append(Subject.teacher_id == teacher_id)
        return filters

        
        
