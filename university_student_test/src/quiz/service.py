from fastapi import HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import desc

from core.models.quiz import Quiz
from core.models.question_quiz import QuestionQuiz
from core.models.questions import Question
from core.models.user import User
from core.models.teacher import Teacher
from core.models.group import Group
from core.models.subject import Subject
from core.utils.basic_service import BasicService
from .schemas import QuizUpdate, QuizBase


class QuizService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.basic_service = BasicService(session)

    async def create_quiz(self, quiz_data: QuizBase):
        """Create quiz + attach correct number of questions."""
        async with self.session.begin():
            # create quiz
            created_quiz = await self.basic_service.create(
                model=Quiz,
                obj_items=quiz_data
            )

            if not created_quiz:
                raise HTTPException(500, "Failed to create quiz")

            # attach questions
            await self.create_quiz_questions(
                quiz_id=created_quiz.id,
                user_id=quiz_data.user_id,
                subject_id=quiz_data.subject_id,
                limit=quiz_data.question_number,
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
            "activate": quiz.is_activate
        }


    async def get_all_quiz(
        self,
        user_id: int,
        is_admin: str | None = None,
        limit: int = 20,
        search: str | None = None,
        offset: int = 0,
        group_id: int | None = None,
    ) -> dict:
        """Retrieve all quizzes with filters and pagination."""
        
        # Helper function to build base filters
        def apply_base_filters(stmt):
            if group_id is not None:
                stmt = stmt.where(Quiz.group_id == group_id)
            elif is_admin != "admin":
                stmt = stmt.where(Quiz.user_id == user_id)
            return stmt
        
        # Helper function to apply search filters
        def apply_search_filters(stmt):
            if search:
                stmt = (
                    stmt
                    .join(Quiz.user)
                    .join(User.teacher)
                    .join(Quiz.group)
                    .join(Quiz.subject)
                    .filter(
                        or_(
                            Teacher.first_name.ilike(f"%{search}%"),
                            Teacher.last_name.ilike(f"%{search}%"),
                            Teacher.patronymic.ilike(f"%{search}%"),
                            Group.name.ilike(f"%{search}%"),
                            Subject.name.ilike(f"%{search}%"),
                            Quiz.quiz_name.ilike(f"%{search}%")
                        )
                    )
                )
            return stmt
        
        # Build count query with all filters
        count_stmt = select(func.count(Quiz.id))
        count_stmt = apply_base_filters(count_stmt)
        count_stmt = apply_search_filters(count_stmt)
        
        # Execute count query
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()
        
        # Build main query
        stmt = (
            select(Quiz)
            .options(
                selectinload(Quiz.user).selectinload(User.teacher),
                selectinload(Quiz.group),
                selectinload(Quiz.subject),
            )
        )
        
        # Apply all filters
        stmt = apply_base_filters(stmt)
        stmt = apply_search_filters(stmt)
        
        # Apply ordering and pagination
        stmt = stmt.order_by(desc(Quiz.id)).limit(limit).offset(offset)
        
        # Execute main query
        result = await self.session.execute(stmt)
        quizzes = result.scalars().all()
        
        # Format data (optimized)
        data = [
            {
                "quiz_id": quiz.id,
                "quiz_name": quiz.quiz_name,
                "quiz_pin": quiz.quiz_pin,
                "user_id": quiz.user_id,
                "teacher_first_name": quiz.user.teacher.first_name if quiz.user and quiz.user.teacher else None,
                "teacher_last_name": quiz.user.teacher.last_name if quiz.user and quiz.user.teacher else None,
                "group_id": quiz.group.id if quiz.group else None,
                "group_name": quiz.group.name if quiz.group else None,
                "subject_id": quiz.subject.id if quiz.subject else None,
                "subject_name": quiz.subject.name if quiz.subject else None,
                "question_number": quiz.question_number,
                "duration": quiz.quiz_time,
                "start_time": quiz.start_time,
                "activate": quiz.is_activate
            }
            for quiz in quizzes
        ]
        
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

    async def create_quiz_questions(self, quiz_id: int, user_id: int, subject_id: int, limit: int):
            """Attach limited number of unique questions to the quiz."""

            # load questions for user + subject
            stmt = select(Question).where(
                Question.user_id == user_id,
                Question.subject_id == subject_id
            )
            questions = (await self.session.execute(stmt)).scalars().all()

            if not questions:
                raise HTTPException(
                    status_code=404,
                    detail="No questions found for this subject"
                )

            # limit number of questions
            questions = questions[:limit]

            # fetch already existing links
            stmt_existing = select(QuestionQuiz.question_id).where(
                QuestionQuiz.quiz_id == quiz_id
            )
            existing_ids = set((await self.session.execute(stmt_existing)).scalars().all())

            # filter new questions
            new_questions = [q for q in questions if q.id not in existing_ids]

            if not new_questions:
                return {"created_links": 0}

            # create new QuestionQuiz entries
            new_links = [
                QuestionQuiz(quiz_id=quiz_id, question_id=q.id)
                for q in new_questions
            ]

            self.session.add_all(new_links)

            return {"created_links": len(new_links)}
    


    async def toggle_active(self, quiz_id: int, active: bool):
        # Get the quiz
        stmt = select(Quiz).where(Quiz.id == quiz_id)
        result = await self.session.execute(stmt)
        quiz_data = result.scalars().first()

        if not quiz_data:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz Data not found"
            )

        # Update the is_activate field
        quiz_data.is_activate = active

        # Commit the changes
        await self.session.commit()

        return quiz_data
