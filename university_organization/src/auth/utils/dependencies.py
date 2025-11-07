import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, status, Depends
from typing import Annotated, Callable
from sqlalchemy.ext.asyncio import AsyncSession

from faststream.rabbit import RabbitBroker
from auth.schemas.auth import TokenPaylod
from auth.utils.security import oauth2_scheme
from core.config import settings
from core.utils.database import db_helper
from core.models.user import User
from .security import get_user  # your local get_user function




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
        user: User | None = await get_user(session=session, username=username)
        if not user:
            return TokenPaylod(valid=False)

    return TokenPaylod(
        valid=True,
        user_id=user.id,
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
    Dependency to protect routes by permissions.

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

