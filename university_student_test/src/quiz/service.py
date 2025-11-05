from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.quiz import Quiz
from core.models.question_quiz import QuestionQuiz
from core.models.questions import Question
from core.utils.basic_service import BasicService
from .schemas import QuizCreate, QuizUpdate, QuizInsert


class QuizService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.basic_service = BasicService(session)

    async def create_quiz(self, quiz_data: QuizCreate):
        """Create a new quiz with calculated end time."""
        end_time = quiz_data.start_time + timedelta(minutes=quiz_data.quiz_time)

        create_data = QuizInsert(
            **quiz_data.model_dump(),
            end_time=end_time
        )

        created_quiz = await self.basic_service.create(model=Quiz, obj_items=create_data)
        if not created_quiz:
            raise HTTPException(
                status_code=500,
                detail="Failed to create quiz"
            )

        await self.create_quiz_question(
            user_id=quiz_data.user_id,
            subject_id=quiz_data.subject_id
        )

        return created_quiz

    async def get_quiz_by_id(
        self,
        quiz_id: int,
        user_id: int,
        is_admin: str | None = None
    ):
        """Get a quiz by ID, checking access permissions."""
        stmt = select(Quiz).where(Quiz.id == quiz_id)
        result = await self.session.execute(stmt)
        quiz = result.scalar_one_or_none()

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )

        if is_admin != "admin" and quiz.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return quiz

    async def get_all_quiz(
        self,
        user_id: int,
        is_admin: str | None = None,
        limit: int = 20,
        offset: int = 0,
        group_id: int | None = None
    ):
        """Retrieve all quizzes, with filters and pagination."""
        stmt = select(Quiz)

        if group_id is not None:
            stmt = stmt.where(Quiz.group_id == group_id)
        elif is_admin != "admin":
            stmt = stmt.where(Quiz.user_id == user_id)

        count_stmt = select(func.count(Quiz.id))
        if group_id is not None:
            count_stmt = count_stmt.where(Quiz.group_id == group_id)
        elif is_admin != "admin":
            count_stmt = count_stmt.where(Quiz.user_id == user_id)

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.scalars(stmt)
        quiz_data = result.all()

        return {
            "total": total,
            "data": quiz_data
        }

    async def update_quiz(
        self,
        quiz_id: int,
        user_id: int,
        quiz_data: QuizUpdate,
        is_admin: str | None = None
    ):
        """Update quiz details."""
        await self.get_quiz_by_id(quiz_id, user_id, is_admin)
        filters = [Quiz.id == quiz_id]
        return await self.basic_service.update(
            model=Quiz,
            filters=filters,
            update_data=quiz_data
        )

    async def delete_quiz(
        self,
        quiz_id: int,
        user_id: int,
        is_admin: str | None = None
    ):
        """Delete a quiz."""
        await self.get_quiz_by_id(quiz_id, user_id, is_admin)
        filters = [Quiz.id == quiz_id]
        return await self.basic_service.delete(model=Quiz, filters=filters)

    async def create_quiz_question(self, user_id: int, subject_id: int):
        """Create question-quiz links for the given user and subject."""
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

        stmt_existing = select(QuestionQuiz.question_id).where(
            QuestionQuiz.quiz_id == quiz.id
        )
        existing_ids = set((await self.session.execute(stmt_existing)).scalars().all())

        new_questions = [q for q in questions if q.id not in existing_ids]

        if not new_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All questions are already linked to this quiz"
            )

        new_links = [
            QuestionQuiz(quiz_id=quiz.id, question_id=q.id)
            for q in new_questions
        ]

        self.session.add_all(new_links)
        await self.session.commit()

        return {"created_links": len(new_links)}
