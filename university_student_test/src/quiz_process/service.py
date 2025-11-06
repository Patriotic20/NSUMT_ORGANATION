from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , func
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from .schemas import ResultCreate , QuizSubmission
from core.models.user import User

from core.utils.basic_service import BasicService
from core.models import Quiz , Question , Result
from core.models.quiz import QuizStatus
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


class QuizProcessService:
    def __init__(self , session: AsyncSession):
        self.session = session
        self.service = BasicService(self.session)


    async def start_quiz(
        self,
        quiz_id: int,
        quiz_pin: str,
        user_id: int,
        group_id: int | None = None
    ) -> dict:
        """Fetch quiz questions for a given quiz ID, PIN, and group."""

        # Fetch student and roles
        student_stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.student),
                selectinload(User.roles)
            )
        )
        student_result = await self.session.execute(student_stmt)
        student_info: User | None = student_result.scalars().first()

        if not student_info or not student_info.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User information or roles missing."
            )

        # Determine user group
        role_name = student_info.roles[0].name
        if role_name == "admin":
            if not group_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Group ID is required for admin users."
                )
            target_group_id = group_id
        else:
            if not student_info.student:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not a student."
                )
            target_group_id = student_info.student.group_id

        # Fetch quiz
        quiz_stmt = (
            select(Quiz)
            .where(
                Quiz.id == quiz_id,
                Quiz.quiz_pin == quiz_pin,
                Quiz.group_id == target_group_id,
            )
            .options(
                selectinload(Quiz.user).selectinload(User.teacher),
                selectinload(Quiz.group),
                selectinload(Quiz.subject),
            )
        )
        quiz_result = await self.session.execute(quiz_stmt)
        quiz: Quiz | None = quiz_result.scalars().first()

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found or inaccessible."
            )

        # Time validation
        tz = ZoneInfo("Asia/Tashkent")
        now = datetime.now(tz)
        start_time = quiz.start_time.replace(tzinfo=tz)
        end_time = quiz.end_time.replace(tzinfo=tz)
        print(now)
        print(start_time)
        print(end_time)

        if now < start_time:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Test has not started yet.",
            )

        if now > end_time:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Test has already finished.",
            )

        # Fetch questions
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

        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No questions available for this quiz."
            )

        # Prepare response
        teacher = getattr(quiz.user, "teacher", None)
        group = getattr(quiz, "group", None)
        subject = getattr(quiz, "subject", None)

        return {
            "user_id": quiz.user_id,
            "teacher_first_name": getattr(teacher, "first_name", None),
            "teacher_last_name": getattr(teacher, "last_name", None),
            "group_id": getattr(group, "id", None),
            "group_name": getattr(group, "name", None),
            "subject_id": getattr(subject, "id", None),
            "subject_name": getattr(subject, "name", None),
            "questions": [q.to_dict(randomize_options=True) for q in questions],
        }


    

    async def end_quiz(self, submission: QuizSubmission, student_id: int):
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
            group_id=quiz_data.group_id,
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
