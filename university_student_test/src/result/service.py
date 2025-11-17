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
            "correct": result_obj.correct_answers,
            "incorrect": result_obj.incorrect_answers,
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
                "name": result_obj.quiz.quiz_name
            } if result_obj.quiz else None,
        }

        return data

    
    async def get_by_field(
        self,
        quiz_id: int | None = None,
    ) -> list[dict]:
        """
        Get all students assigned to a quiz with their results.
        """

        stmt = (
            select(Result)
            .options(
                selectinload(Result.student).selectinload(User.student),
                selectinload(Result.group),
                selectinload(Result.subject),
                selectinload(Result.quiz),
            )
        )
        
        if quiz_id:
            stmt = stmt.where(Result.quiz_id == quiz_id)
        
        # Execute query
        result = await self.session.execute(stmt)
        results = result.scalars().all()
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No results found"
            )
        
        # Build response data
        data = []
        for res in results:
            student_user = res.student.student if res.student else None
            
            item = {
                "student": {
                    "id": res.student_id,
                    "first_name": student_user.first_name if student_user else None,
                    "last_name": student_user.last_name if student_user else None,
                    "third_name": student_user.third_name if student_user else None,
                } if res.student else None,
                "group": {
                    "id": res.group_id,
                    "name": res.group.name
                } if res.group else None,
                "subject": {
                    "id": res.subject_id,
                    "name": res.subject.name
                } if res.subject else None,
                "quiz": {
                    "id": res.quiz_id,
                    "name": res.quiz.quiz_name
                } if res.quiz else None,
                "result": {
                    "id": res.id,
                    "correct_answers": res.correct_answers,
                    "incorrect_answers": res.incorrect_answers,
                    "grade": res.grade,
                }
            }
            data.append(item)
        
        return data

    async def get_all(
        self,
        user_id: int,
        is_admin: str | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> dict[str, list[dict] | int]:
        """
        Retrieve only the latest (most recent) result per student.
        Admins see all, non-admins only their results.
        """
        # --- STEP 1: Subquery: get latest created_at per student ---
        latest_subq = (
            select(
                Result.student_id,
                func.max(Result.created_at).label("latest_created_at")
            )
            .group_by(Result.student_id)
            .subquery()  # ✅ ADD THIS!
        )
        
        # --- STEP 2: Join subquery to main table to get full Result rows ---
        stmt = (
            select(Result)
            .join(
                latest_subq,
                (Result.student_id == latest_subq.c.student_id)
                & (Result.created_at == latest_subq.c.latest_created_at)
            )
            .options(
                selectinload(Result.student).selectinload(User.student),
                selectinload(Result.group),
                selectinload(Result.subject),
                selectinload(Result.quiz),
            )
            .order_by(Result.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        # --- STEP 3: Filter for non-admin users ---
        if is_admin != "admin":
            stmt = stmt.where(Result.teacher_id == user_id)
        
        # --- STEP 4: Count how many unique students have results ---
        count_stmt = select(func.count(func.distinct(Result.student_id)))
        
        if is_admin != "admin":
            count_stmt = count_stmt.where(Result.teacher_id == user_id)
        
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # --- STEP 5: Execute main query ---
        result = await self.session.execute(stmt)
        results = result.scalars().all()
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No results found"
            )
        
        # --- STEP 6: Transform into list of dicts ---
        data = []
        for r in results:
            student_user = r.student.student if r.student else None
            item = {
                "id": r.id,
                "grade": r.grade,
                "correct": r.correct_answers,
                "incorrect": r.incorrect_answers,
                "created_at": r.created_at.isoformat(),
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
                    "name": r.quiz.quiz_name
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
