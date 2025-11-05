from typing import list, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.results import Result


class ResultService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int, user_id: int, is_admin: Optional[str] = None) -> Result:
        """
        Retrieve a single result by ID.
        
        Admins can access any result; non-admins only their own.
        """
        stmt = select(Result).where(Result.id == id)
        result = await self.session.execute(stmt)
        result_obj = result.scalar_one_or_none()

        if not result_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Result not found"
            )

        if is_admin != "admin" and result_obj.teacher_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return result_obj

    async def get_all(
        self,
        user_id: int,
        is_admin: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> dict[str, list[Result] | int]:
        """
        Retrieve all results with pagination.

        Admins can see all results; non-admins only their own.
        Returns a dict with total count and data list.
        """
        stmt = select(Result)

        if is_admin != "admin":
            stmt = stmt.where(Result.teacher_id == user_id)

        # Get total count
        count_stmt = select(Result)
        if is_admin != "admin":
            count_stmt = count_stmt.where(Result.teacher_id == user_id)

        total_result = await self.session.execute(count_stmt)
        total = len(total_result.scalars().all())

        # Apply pagination
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        result_data = result.scalars().all()

        if not result_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No results found"
            )

        return {"total": total, "data": result_data}

    async def delete(self, id: int, user_id: int, is_admin: Optional[str] = None) -> dict[str, str]:
        """
        Delete a result by ID.

        Admins can delete any result; non-admins only their own.
        """
        result_obj = await self.get_by_id(id=id, user_id=user_id, is_admin=is_admin)

        await self.session.delete(result_obj)
        await self.session.commit()

        return {"message": "Deleted successfully"}
