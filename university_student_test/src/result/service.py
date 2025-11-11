from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.results import Result
from core.models.user_answer import UserAnswer
from sqlalchemy.orm import selectinload
from core.models.questions import Question
from sqlalchemy import func

from core.models.student import Student
from core.models.user import User

class ResultService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
        
    async def get_users_answers(self, user_id: int):
        stmt = (
            select(UserAnswer)
            .where(UserAnswer.user_id == user_id)
            .options(selectinload(UserAnswer.question))
        )

        result = await self.session.execute(stmt)
        user_answers = result.scalars().all()

        return [
            {
                "question_id": ua.question_id,
                "question_text": ua.question.text,
                "correct_answers": ua.question.option_a,  
                "selected_option": ua.options,
                "option_a": ua.question.option_a,
                "option_b": ua.question.option_b,
                "option_c": ua.question.option_c,
                "option_d": ua.question.option_d,
            }
            for ua in user_answers
        ]


        

    async def get_by_id(
        self,
        id: int,
        user_id: int,
        is_admin: Optional[str] = None
    ) -> dict:
        """
        Retrieve a single result by ID with related fields.
        Admins can access any result; non-admins only their own.
        """

        # Load result with related entities
        stmt = (
            select(Result)
            .where(Result.id == id)
            .options(
                selectinload(Result.student).selectinload(User.student),
                selectinload(Result.group),
                selectinload(Result.subject),
                selectinload(Result.quiz),
            )
        )
        result = await self.session.execute(stmt)
        result_obj = result.scalar_one_or_none()

        if not result_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Result not found"
            )

        # Check access permissions for non-admins
        if is_admin != "admin" and result_obj.teacher_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Prepare structured response (same style as get_all)
        student_user = result_obj.student.student if result_obj.student else None

        data = {
            "id": result_obj.id,
            "grade": result_obj.grade,
            "student": {
                "id": result_obj.student_id,
                "first_name": student_user.first_name if student_user else None,
                "last_name": student_user.last_name if student_user else None,
                "third_name": student_user.third_name if student_user else None,
            } if result_obj.student else None,
            "group": {
                "id": result_obj.group_id,
                "name": result_obj.group.name
            } if result_obj.group else None,
            "subject": {
                "id": result_obj.subject_id,
                "name": result_obj.subject.name
            } if result_obj.subject else None,
            "quiz": {
                "id": result_obj.quiz_id,
                "name": result_obj.quiz.name
            } if result_obj.quiz else None,
        }

        return data

    
    async def get_by_filed(
        self,
        student_id: int | None = None,
        teacher_id: int | None = None,
        group_id: int | None = None,
        subject_id: int | None = None,
        quiz_id: int | None = None,
    ) -> list[dict]:
        """
        Group results by student_id and return structured data.
        """

        # Base query — we’ll group by student
        stmt = (
            select(
                Result.student_id,
                func.array_agg(Result.id).label("result_ids")  # Collect all result IDs for each student
            )
        )

        # Apply filters
        if student_id:
            stmt = stmt.where(Result.student_id == student_id)
        if teacher_id:
            stmt = stmt.where(Result.teacher_id == teacher_id)
        if group_id:
            stmt = stmt.where(Result.group_id == group_id)
        if subject_id:
            stmt = stmt.where(Result.subject_id == subject_id)
        if quiz_id:
            stmt = stmt.where(Result.quiz_id == quiz_id)

        # Group by student_id
        stmt = stmt.group_by(Result.student_id)

        # Execute
        result = await self.session.execute(stmt)
        grouped_rows = result.all()

        if not grouped_rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No results found"
            )

        data = []

        # For each student_id, load details (name, group, subject, quiz)
        for row in grouped_rows:
            student_id = row.student_id
            result_ids = row.result_ids

            # Fetch one result to get related objects (group, subject, etc.)
            detail_stmt = (
                select(Result)
                .where(Result.id.in_(result_ids))
                .options(
                    selectinload(Result.student).selectinload(User.student),
                    selectinload(Result.group),
                    selectinload(Result.subject),
                    selectinload(Result.quiz),
                )
            )

            details_result = await self.session.execute(detail_stmt)
            results = details_result.scalars().all()

            # Use first result for student/group/subject/quiz data (since all same student)
            first = results[0]
            student_user = first.student.student if first.student else None

            item = {
                "student": {
                    "id": first.student_id,
                    "first_name": student_user.first_name if student_user else None,
                    "last_name": student_user.last_name if student_user else None,
                    "third_name": student_user.third_name if student_user else None,
                } if first.student else None,
                "group": {
                    "id": first.group_id,
                    "name": first.group.name
                } if first.group else None,
                "subject": {
                    "id": first.subject_id,
                    "name": first.subject.name
                } if first.subject else None,
                "quiz": {
                    "id": first.quiz_id,
                    "name": first.quiz.name
                } if first.quiz else None,
                "result_ids": result_ids,
            }

            data.append(item)

        return data

    async def get_all(
        self,
        user_id: int,
        is_admin: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> dict[str, list[dict] | int]:
        """
        Retrieve all results with pagination, including specific related fields.
        """

        # Base query
        stmt = select(Result).options(
            selectinload(Result.student).selectinload(User.student),  
            selectinload(Result.group),
            selectinload(Result.subject),
            selectinload(Result.quiz),
        )

        # Non-admins see only their results
        if is_admin != "admin":
            stmt = stmt.where(Result.teacher_id == user_id)

        # Total count efficiently
        count_stmt = select(func.count(Result.id))
        if is_admin != "admin":
            count_stmt = count_stmt.where(Result.teacher_id == user_id)

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0  # integer count

        # Pagination
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        results = result.scalars().all()

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No results found"
            )

        # Transform results to dict with required fields
        data = []
        for r in results:
            student_user = r.student.student if r.student else None

            item = {
                "id": r.id,
                "grade": r.grade,
                "student": {
                    "id": r.student_id,
                    "first_name": student_user.first_name if student_user else None,
                    "last_name": student_user.last_name if student_user else None,
                    "third_name": student_user.third_name if student_user else None,
                } if r.student else None,
                "group": {
                    "id": r.group_id,
                    "name": r.group.name
                } if r.group else None,
                "subject": {
                    "id": r.subject_id,
                    "name": r.subject.name
                } if r.subject else None,
                "quiz": {
                    "id": r.quiz_id,
                    "name": r.quiz.name
                } if r.quiz else None,
            }
            data.append(item)

        return {"total": total, "data": data}
    

    async def delete(self, id: int, user_id: int, is_admin: Optional[str] = None) -> dict[str, str]:
        """
        Delete a result by ID.

        Admins can delete any result; non-admins only their own.
        """
        result_obj = await self.get_by_id(id=id, user_id=user_id, is_admin=is_admin)

        await self.session.delete(result_obj)
        await self.session.commit()

        return {"message": "Deleted successfully"}
