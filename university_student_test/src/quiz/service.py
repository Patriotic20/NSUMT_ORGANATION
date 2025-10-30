from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from pathlib import Path
import uuid


from .schemas import QuizBase, QuizUpdate
from core.utils.basic_service import BasicService
from core.models import Quiz
from core.config import settings


class QuizService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.basic_service = BasicService(session)

    async def create_quiz(self, quiz_data: QuizBase):
        return await self.basic_service.create(model=Quiz, obj_items=quiz_data)

    async def get_quiz_by_id(self, quiz_id: int):
        return await self.check_by_teacher_id(
            quiz_id=quiz_id, 
            raise_not_found=True
        )
        

    async def get_all_quiz(
        self,
        limit: int = 20, 
        offset: int = 0,
    ):
        return await self.check_by_teacher_id(
            limit=limit,
            offset=offset,
            is_all=True,
            raise_not_found=True,
        )

    async def update_quiz(
        self, 
        quiz_id: int, 
        quiz_data: QuizUpdate
    ):
        await self.check_by_teacher_id(
            quiz_id=quiz_id,  
            raise_not_found=True
            )
        filters = [Quiz.id == quiz_id]
        return await self.basic_service.update(model=Quiz, filters=filters, update_data=quiz_data)
        
        
                
    async def delete_quiz(self, quiz_id: int):
        await self.check_by_teacher_id(
            quiz_id=quiz_id, 
            raise_not_found=True
        )
        filters = [Quiz.id == quiz_id]
        return await self.basic_service.delete(model=Quiz, filters=filters)

    async def check_by_teacher_id(
        self,
        limit: int | None = None,
        offset: int = 0,
        quiz_id: int | None = None,
        is_all: bool = False,
        raise_not_found: bool = False,
    ):
        filters = []
        if quiz_id is not None:
            filters.append(Quiz.id == quiz_id)

        stmt = select(Quiz)

        if filters:
            stmt = stmt.where(and_(*filters))

        if limit is not None:
            stmt = stmt.limit(limit)

        if offset:
            stmt = stmt.offset(offset)

        result = await self.session.execute(stmt)
        scalars = result.scalars()
        data = scalars.all() if is_all else scalars.first()

        if raise_not_found and not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz(s) not found",
            )

        return data
