from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Annotated, Callable

import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from auth.schemas.auth import TokenPaylod  
from core.config import settings
from core.database.db_helper import db_helper
from core.models.user import User
from core.models.role import Role
from core.models.student import Student

oauth2_scheme = APIKeyHeader(name="Authorization")

async def get_user(session: AsyncSession, username: str) -> User:
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
            detail="User not found",
        )
    return user_data

async def validate_token_subscriber(token: str) -> TokenPaylod:
    try:
        payload = jwt.decode(
            token,
            settings.jwt.access_secret_key,
            algorithms=[settings.jwt.algorithm],
        )
        username = payload.get("username")
        if not username:
            return TokenPaylod(valid=False)
    except InvalidTokenError:
        return TokenPaylod(valid=False)

    async with db_helper.session_factory() as session:
        user: User | None = await get_user(session, username=username)
        
        stmt = select(Student).where(Student.user_id == user.id)
        result = await session.execute(stmt)
        student_data = result.scalar_one_or_none()
        
        if not user:
            return TokenPaylod(valid=False)

    return TokenPaylod(
        valid=True,
        user_id=user.id,
        group_id=student_data.group_id,
        username=user.username,
        role=user.roles[0].name if user.roles else None,
        permissions=[p.name for r in user.roles for p in r.permissions],
    )

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> TokenPaylod:
    payload = await validate_token_subscriber(token)

    if not payload.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return payload

def require_permission(*permissions: str, any_of: bool = True) -> Callable:
    """
    Dependency to protect routes by required permissions.

    """
    async def checker(user: TokenPaylod = Depends(get_current_user)) -> TokenPaylod:
        user_perms = set(user.permissions or [])

        if any_of:
            if not any(p in user_perms for p in permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied",
                )
        else:
            if not all(p in user_perms for p in permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied",
                )

        return user

    return checker
