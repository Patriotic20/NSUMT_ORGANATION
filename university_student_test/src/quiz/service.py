from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models.quiz import Quiz
from core.models.question_quiz import QuestionQuiz
from core.models.questions import Question
from core.models.user import User
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
        is_admin: str | None = None,
    ) -> dict:
        """Get a quiz by ID with related teacher, group, and subject info."""

        stmt = (
            select(Quiz)
            .where(Quiz.id == quiz_id)
            .options(
                selectinload(Quiz.user).selectinload(User.teacher),
                selectinload(Quiz.group),
                selectinload(Quiz.subject),
            )
        )

        result = await self.session.execute(stmt)
        quiz: Quiz = result.scalar_one_or_none()

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )

        # Access control
        if is_admin != "admin" and quiz.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Safely get related data
        teacher = getattr(quiz.user, "teacher", None)
        group = getattr(quiz, "group", None)
        subject = getattr(quiz, "subject", None)

        teacher_first_name = getattr(teacher, "first_name", None)
        teacher_last_name = getattr(teacher, "last_name", None)
        group_id = getattr(group, "id", None)
        group_name = getattr(group, "name", None)
        subject_id = getattr(subject, "id", None)
        subject_name = getattr(subject, "name", None)

        # Return structured data
        return {
            "quiz_id": quiz.id,
            "quiz_pin": quiz.quiz_pin,
            "user_id": quiz.user_id,
            "teacher_first_name": teacher_first_name,
            "teacher_last_name": teacher_last_name,
            "group_id": group_id,
            "group_name": group_name,
            "subject_id": subject_id,
            "subject_name": subject_name,
            "quiz_name": quiz.quiz_name,
            "question_number": quiz.question_number,
            "duration": quiz.quiz_time,
            "start_time": quiz.start_time,
            "end_time": quiz.end_time,
            "current_status": quiz.status,
        }


    async def get_all_quiz(
        self,
        user_id: int,
        is_admin: str | None = None,
        limit: int = 20,
        offset: int = 0,
        group_id: int | None = None,
    ) -> dict:
        """Retrieve all quizzes with filters and pagination."""

        # Base query with relationships
        stmt = (
            select(Quiz)
            .options(
                selectinload(Quiz.user).selectinload(User.teacher),
                selectinload(Quiz.group),
                selectinload(Quiz.subject),
            )
        )

        # Apply filters
        if group_id is not None:
            stmt = stmt.where(Quiz.group_id == group_id)
        elif is_admin != "admin":
            stmt = stmt.where(Quiz.user_id == user_id)

        # Total count (for pagination)
        count_stmt = select(func.count(Quiz.id))
        if group_id is not None:
            count_stmt = count_stmt.where(Quiz.group_id == group_id)
        elif is_admin != "admin":
            count_stmt = count_stmt.where(Quiz.user_id == user_id)

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        # Pagination
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        quizzes = result.scalars().all()

        # Format data
        data = []
        for quiz in quizzes:
            teacher = getattr(quiz.user, "teacher", None)
            group = getattr(quiz, "group", None)
            subject = getattr(quiz, "subject", None)

            data.append({
                "quiz_id": quiz.id,
                "quiz_name": quiz.quiz_name,
                "quiz_pin": quiz.quiz_pin,
                "user_id": quiz.user_id,
                "teacher_first_name": getattr(teacher, "first_name", None),
                "teacher_last_name": getattr(teacher, "last_name", None),
                "group_id": getattr(group, "id", None),
                "group_name": getattr(group, "name", None),
                "subject_id": getattr(subject, "id", None),
                "subject_name": getattr(subject, "name", None),
                "question_number": quiz.question_number,
                "duration": quiz.quiz_time,
                "start_time": quiz.start_time,
                "end_time": quiz.end_time,
                "current_status": quiz.status,
            })

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": data,
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
