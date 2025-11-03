from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from pathlib import Path
import uuid


from .schemas import QuizBase, QuizUpdate, QuestionQuizCreate, QuizCreate
from core.utils.basic_service import BasicService
from core.models import Quiz
from core.models.questions import Question
from core.config import settings


from core.models.question_quiz import QuestionQuiz


class QuizService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.basic_service = BasicService(session)

    async def create_quiz(self, quiz_data: QuizCreate):
        # Convert Pydantic to dict for ORM
        quiz_dict = quiz_data.model_dump()

        # 1️⃣ Create the quiz
        created_quiz = await self.basic_service.create(model=Quiz, obj_items=quiz_dict)
        if not created_quiz:
            raise HTTPException(
                status_code=500,
                detail="Failed to create quiz"
            )

        # 2️⃣ Create QuestionQuiz links
        await self.create_quiz_question(
            user_id=quiz_data.user_id,
            subject_id=quiz_data.subject_id
        )

        return created_quiz


    async def get_quiz_by_id(self, quiz_id: int):
        return await self.check_by_teacher_id(
            quiz_id=quiz_id, 
            raise_not_found=True
        )
        

    async def get_all_quiz(
        self,
        limit: int = 20, 
        offset: int = 0,
        group_id: int | None = None
    ):
        stmt = select(Quiz)

        # ✅ Apply filter only if group_id is provided
        if group_id is not None:
            stmt = stmt.where(Quiz.group_id == group_id)

        
        # ✅ Apply pagination
        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.scalars(stmt)
        return result.all()
        
        

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
    
    
    
    async def create_quiz_question(self, user_id: int, subject_id: int):
        # 1️⃣ Get all questions for this user and subject
        stmt = select(Question).where(
            Question.user_id == user_id,
            Question.subject_id == subject_id
        )
        questions = (await self.session.execute(stmt)).scalars().all()
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No questions found for this subject"
            )

        # 2️⃣ Get the quiz for this user and subject
        stmt_quiz = select(Quiz).where(
            Quiz.user_id == user_id,
            Quiz.subject_id == subject_id
        )
        quiz = (await self.session.execute(stmt_quiz)).scalars().first()
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found for this subject"
            )

        # 3️⃣ Get all existing question-quiz links in one go
        stmt_existing = select(QuestionQuiz.question_id).where(
            QuestionQuiz.quiz_id == quiz.id
        )
        existing_ids = set((await self.session.execute(stmt_existing)).scalars().all())

        # 4️⃣ Filter out questions already linked
        new_questions = [q for q in questions if q.id not in existing_ids]
        if not new_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All questions are already linked to this quiz"
            )

        # 5️⃣ Bulk create new QuestionQuiz links
        new_links = [
            QuestionQuiz(quiz_id=quiz.id, question_id=q.id)
            for q in new_questions
        ]
        self.session.add_all(new_links)
        await self.session.commit()

        return {"created_links": len(new_links)}
