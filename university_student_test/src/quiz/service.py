from fastapi import HTTPException, status
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from core.models.quiz import Quiz
from core.utils.basic_service import BasicService
from core.models.question_quiz import QuestionQuiz
from core.models.questions import Question

from .schemas import QuizCreate, QuizUpdate

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
            raise HTTPException(status_code=500, detail="Failed to create quiz")

        # 2️⃣ Create QuestionQuiz links
        await self.create_quiz_question(
            user_id=quiz_data.user_id,
            subject_id=quiz_data.subject_id
        )

        return created_quiz

    async def get_quiz_by_id(self, quiz_id: int, user_id: int, is_admin: str | None = None):
        stmt = select(Quiz).where(Quiz.id == quiz_id)
        result = await self.session.execute(stmt)
        quiz = result.scalar_one_or_none()

        if not quiz:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

        # Check permissions: owner or admin
        if is_admin != "admin" and quiz.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        return quiz

    async def get_all_quiz(
        self,
        user_id: int,
        is_admin: str | None = None,
        limit: int = 20,
        offset: int = 0,
        group_id: int | None = None
    ):
        stmt = select(Quiz)

        # Conditional filtering
        if group_id is not None:
            stmt = stmt.where(Quiz.group_id == group_id)
        else:
            # Only show quizzes for this user if not admin
            if is_admin != "admin":
                stmt = stmt.where(Quiz.user_id == user_id)

        # Pagination
        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.scalars(stmt)
        return result.all()


    async def update_quiz(
        self,
        quiz_id: int,
        user_id: int,
        quiz_data: QuizUpdate,
        is_admin: str | None = None,
    ):
        quiz = await self.get_quiz_by_id(quiz_id, user_id, is_admin)

        # Only admin or owner can update
        filters = [Quiz.id == quiz_id]
        return await self.basic_service.update(model=Quiz, filters=filters, update_data=quiz_data)

    async def delete_quiz(
        self,
        quiz_id: int,
        user_id: int,
        is_admin: str | None = None,
    ):
        quiz = await self.get_quiz_by_id(quiz_id, user_id, is_admin)

        filters = [Quiz.id == quiz_id]
        return await self.basic_service.delete(model=Quiz, filters=filters)


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
