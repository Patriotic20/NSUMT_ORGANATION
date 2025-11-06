from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , func
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from .schemas import ResultCreate , QuizSubmission
from core.models.user import User

from core.utils.basic_service import BasicService
from core.models import Quiz , Question , Result
from core.models.quiz import QuizStatus


class QuizProcessService:
    def __init__(self , session: AsyncSession):
        self.session = session
        self.service = BasicService

    async def start_quiz(
        self,
        quiz_id: int,
        quiz_pin: str,
        group_id: int,
    ) -> dict | None:
        """
        Fetch quiz questions for a given quiz ID, PIN, and group.

        Raises:
            HTTPException: If quiz is not started or already finished.

        Returns:
            Dictionary containing quiz info and randomized question data.
        """

        # Fetch quiz with related data
        stmt = (
            select(Quiz)
            .where(
                Quiz.id == quiz_id,
                Quiz.quiz_pin == quiz_pin,
                Quiz.group_id == group_id,
            )
            .options(
                selectinload(Quiz.user).selectinload(User.teacher),
                selectinload(Quiz.group),
                selectinload(Quiz.subject),
            )
        )
        result = await self.session.execute(stmt)
        quiz: Quiz | None = result.scalars().first()

        if not quiz:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Peroblem here"
            )

        # Check quiz status
        if quiz.current_status == QuizStatus.NOT_STARTED:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Test has not started yet.",
            )

        if quiz.current_status == QuizStatus.FINISHED:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Test has already finished.",
            )

        # Fetch random questions
        stmt_questions = (
            select(Question)
            .where(
                Question.user_id == quiz.user_id,
                Question.subject_id == quiz.subject_id,
            )
            .order_by(func.random())
            .limit(quiz.question_number)
        )
        result = await self.session.execute(stmt_questions)
        questions = result.scalars().all()

        # Prepare related info
        teacher = getattr(quiz.user, "teacher", None)
        group = getattr(quiz, "group", None)
        subject = getattr(quiz, "subject", None)

        teacher_first_name = getattr(teacher, "first_name", None)
        teacher_last_name = getattr(teacher, "last_name", None)
        group_id = getattr(group, "id", None)
        group_name = getattr(group, "name", None)
        subject_id = getattr(subject, "id", None)
        subject_name = getattr(subject, "name", None)

        # Convert questions to dicts with randomized options
        data = [q.to_dict(randomize_options=True) for q in questions]

        return {
            "user_id": quiz.user_id,
            "teacher_first_name": teacher_first_name,
            "teacher_last_name": teacher_last_name,
            "group_id": group_id,
            "group_name": group_name,
            "subject_id": subject_id,
            "subject_name": subject_name,
            "questions": data,
        }
    

    async def end_quiz(self, submission: QuizSubmission, student_id: int, group_id: int):
        """Process quiz submission, calculate score, and save result."""

        # Fetch quiz
        quiz_stmt = select(Quiz).where(Quiz.id == submission.quiz_id)
        quiz_result = await self.session.execute(quiz_stmt)
        quiz_data = quiz_result.scalars().first()

        if not quiz_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found."
            )

        # Validate quiz status
        if quiz_data.current_status.name == "NOT_STARTED":
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Quiz has not started yet."
            )

        if quiz_data.current_status.name == "FINISHED":
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Quiz has already finished."
            )

        # Fetch all submitted questions
        submitted_ids = [q.id for q in submission.questions]
        stmt = select(Question).where(Question.id.in_(submitted_ids))
        result = await self.session.execute(stmt)
        question_records = {q.id: q for q in result.scalars().all()}

        correct_count = 0
        incorrect_count = 0

        for q in submission.questions:
            question = question_records.get(q.id)
            if not question:
                continue
            if q.option == question.option_a:
                correct_count += 1
            else:
                incorrect_count += 1

        total = correct_count + incorrect_count
        percentage = (100 * correct_count / total) if total else 0

        # Grade logic
        if percentage >= 86:
            grade = 5
        elif percentage >= 76:
            grade = 4
        elif percentage >= 56:
            grade = 3
        else:
            grade = 2

        # Build result data
        result_data = ResultCreate(
            student_id=student_id,
            teacher_id=quiz_data.user_id,
            subject_id=quiz_data.subject_id,
            group_id=group_id,
            quiz_id=submission.quiz_id,
            grade=grade,
            correct_answers=correct_count,
            incorrect_answers=incorrect_count
        )

        # Save to DB
        await self.service.create(model=Result, obj_items=result_data)

        return {
            "summary": {
                "quiz_id": submission.quiz_id,
                "total_answered": total,
                "correct_answers": correct_count,
                "incorrect_answers": incorrect_count,
                "grade": grade,
                "percentage": percentage
            }
        }
