from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from fastapi import HTTPException, status
from fastapi.security import  APIKeyHeader 

from core.models import User, Role



oauth2_scheme = APIKeyHeader(name="Authorization")


async def get_user(session: AsyncSession, username: str):
    stmt = (
        select(User)
        .where(User.username == username)
        .options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
    )
    result = await session.execute(stmt)
    user_data = result.scalars().first()
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user_data







