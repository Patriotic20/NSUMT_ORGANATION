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


    async def create_questions(self, quiz_id: int, quiz_pin: str):
        # Fetch quiz by ID + PIN
        stmt = select(Quiz).where(
            Quiz.id == quiz_id,
            Quiz.quiz_pin == quiz_pin
        )
        result = await self.session.execute(stmt)
        quiz: Quiz | None = result.scalars().first()

        if not quiz:
            return None

        # Use dynamic property current_status
        if quiz.current_status == QuizStatus.NOT_STARTED:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Test has not started yet."
            )

        if quiz.current_status == QuizStatus.FINISHED:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Test has already finished."
            )

        # Fetch random questions
        stmt = (
            select(Question)
            .order_by(func.random())
            .limit(quiz.question_number)
        )
        result = await self.session.execute(stmt)
        questions = result.scalars().all()

        return [q.to_dict(randomize_options=True) for q in questions]        
    
    async def take_questions(self, submission: QuizSubmission, student_id: int):
        submitted_question_ids = [q.id for q in submission.questions]

        stmt = select(Question).where(Question.id.in_(submitted_question_ids))
        result = await self.session.execute(stmt)
        question_records_by_id = {q.id: q for q in result.scalars().all()}

        correct_answer_count = 0
        incorrect_answer_count = 0

        for submitted_question in submission.questions:
            question_record = question_records_by_id.get(submitted_question.id)
            if not question_record:
                continue

            if submitted_question.option == question_record.option_a:
                correct_answer_count += 1
            elif submitted_question.option == question_record.option_a_image:
                correct_answer_count += 1
            else:
                incorrect_answer_count += 1

        total_answered_count = correct_answer_count + incorrect_answer_count
        percentage: float = (100 * correct_answer_count) / total_answered_count if total_answered_count else 0

        if percentage >= 86:
            grade = 5
        elif percentage >= 76:
            grade = 4
        elif percentage >= 56:
            grade = 3
        else:
            grade = 2  

        # build result object
        result_data = ResultCreate(
            student_id=student_id,
            quiz_id=submission.quiz_id,
            grade=grade,
            correct_answers=correct_answer_count,
            incorrect_answers=incorrect_answer_count
        )

        # save result
        await self.service.create(model=Result, obj_items=result_data)

        # return summary
        return {
            "summary": {
                "quiz_id": submission.quiz_id,
                "total_answered": total_answered_count,
                "correct_answers": correct_answer_count,
                "incorrect_answers": incorrect_answer_count,
                "grade": grade,
                "percentage": percentage
            }
        }

