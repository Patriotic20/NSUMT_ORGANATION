from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from fastapi.security import  APIKeyHeader 

from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext

import jwt

from core.config import settings
from core.models import User, Role




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = APIKeyHeader(name="Authorization")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


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
    
    return user_data



def _create_token(data: dict, secret_key: str, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.jwt.algorithm)
    return encoded_jwt


def create_access_token(data: dict):
    delta = timedelta(minutes=settings.jwt.access_secret_minutes)
    return _create_token(
        data=data, secret_key=settings.jwt.access_secret_key, expires_delta=delta
    )


def create_refresh_token(data: dict):
    delta = timedelta(days=settings.jwt.refresh_secret_day)
    return _create_token(
        data=data, secret_key=settings.jwt.refresh_secret_key, expires_delta=delta
    )



