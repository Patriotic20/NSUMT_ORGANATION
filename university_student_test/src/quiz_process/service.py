from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , func
from fastapi import HTTPException, status

from .schemas import ResultCreate , QuizSubmission

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
    ) -> list[dict] | None:
        """
        Fetch quiz questions for a given quiz ID, PIN, and group.

        Raises:
            HTTPException: If quiz is not started or already finished.
        
        Returns:
            List of question dictionaries with randomized options.
        """
        # Fetch quiz by ID, PIN, and group
        stmt = select(Quiz).where(
            Quiz.id == quiz_id,
            Quiz.quiz_pin == quiz_pin,
            Quiz.group_id == group_id,
        )
        result = await self.session.execute(stmt)
        quiz: Quiz | None = result.scalars().first()

        if not quiz:
            return None

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

        # Fetch random questions for this quiz
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

        # Return as list of dicts with randomized options
        return [q.to_dict(randomize_options=True) for q in questions]
    
    

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
