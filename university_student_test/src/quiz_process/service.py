from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , func
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from .schemas import ResultCreate , QuizSubmission, UserAnswerCreate
from core.models.user import User
from core.models.user_answer import UserAnswer
from core.models.question_quiz import QuestionQuiz

from core.utils.basic_service import BasicService
from core.models import Quiz , Question , Result
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import insert

from core.logging import logging


logger = logging.getLogger(__name__)

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
        # Fetch student + roles
        student_stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.student),
                selectinload(User.roles)
            )
        )
        student = (await self.session.execute(student_stmt)).scalars().first()
        if not student or not student.roles:
            raise HTTPException(status_code=403, detail="User information or roles missing.")
        
        # Determine group
        role_name = student.roles[0].name
        if role_name == "admin":
            if not group_id:
                raise HTTPException(status_code=400, detail="Group ID required for admin.")
            target_group_id = group_id
        else:
            if not student.student:
                raise HTTPException(status_code=403, detail="User is not a student.")
            target_group_id = student.student.group_id
        
        # Fetch quiz
        quiz_stmt = (
            select(Quiz)
            .where(
                Quiz.id == quiz_id,
                Quiz.quiz_pin == quiz_pin,
                Quiz.group_id == target_group_id
            )
            .options(
                selectinload(Quiz.user).selectinload(User.teacher),
                selectinload(Quiz.group),
                selectinload(Quiz.subject)
            )
        )
        quiz = (await self.session.execute(quiz_stmt)).scalars().first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found or inaccessible.")
        if not quiz.is_activate:
            raise HTTPException(status_code=405, detail="Test is not active.")
        
        # Time validation
        tz = ZoneInfo("Asia/Tashkent")
        now = datetime.now(tz)
        start_time = quiz.start_time.replace(tzinfo=tz)
        if now < start_time:
            raise HTTPException(status_code=403, detail="Test has not started yet.")
        
        # ================================
        # FIXED: Fetch questions through QuestionQuiz junction table
        # ================================
        stmt_questions = (
            select(Question)
            .join(QuestionQuiz, QuestionQuiz.question_id == Question.id)
            .where(QuestionQuiz.quiz_id == quiz.id)
            .order_by(func.random())
            .limit(quiz.question_number)
        )
        questions = (await self.session.execute(stmt_questions)).scalars().all()
        
        if not questions:
            raise HTTPException(status_code=404, detail="No questions for this quiz.")
        
        teacher = getattr(quiz.user, "teacher", None)
        return {
            "user_id": quiz.user_id,
            "teacher_first_name": getattr(teacher, "first_name", None),
            "teacher_last_name": getattr(teacher, "last_name", None),
            "group_id": quiz.group.id if quiz.group else None,
            "group_name": quiz.group.name if quiz.group else None,
            "subject_id": quiz.subject.id if quiz.subject else None,
            "subject_name": quiz.subject.name if quiz.subject else None,
            "duration": quiz.quiz_time,
            "questions": [q.to_dict(randomize_options=True) for q in questions]
        }



    

    async def end_quiz(self, submission: QuizSubmission, student_id: int):
        """Process quiz submission, calculate score, and save result."""

        await self.save_user_answers(submission = submission, user_id = student_id)

        # Fetch quiz
        quiz_stmt = select(Quiz).where(Quiz.id == submission.quiz_id)
        quiz_result = await self.session.execute(quiz_stmt)
        quiz_data = quiz_result.scalars().first()

        if not quiz_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found."
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
        percentage = (100 * correct_count / quiz_data.question_number) if quiz_data.question_number else 0

        # Grade logic
        if percentage >= 86:
            grade = 5
        elif percentage >= 72:
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

        logger.info(
            f"QUIZ_PROCESS_END | "
            f"user_id={student_id} | "
            f"quiz_id={submission.quiz_id} | "
            f"subject_id={quiz_data.subject_id} | "
            f"group_id={quiz_data.group_id} | "
            f"teacher_id={quiz_data.user_id} | "
            f"total_answered={total} | "
            f"correct={correct_count} | "
            f"incorrect={incorrect_count} | "
            f"percentage={percentage:.2f} | "
            f"grade={grade}"
        )

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
        
        

    async def save_user_answers(self, submission: QuizSubmission, user_id: int):
        
        stmt = insert(UserAnswer).values([
            {
                "quiz_id": submission.quiz_id,
                "user_id": user_id,
                "question_id": q.id,
                "options": q.option
            }
            for q in submission.questions
        ])
        
        await self.session.execute(stmt)
        await self.session.commit()
