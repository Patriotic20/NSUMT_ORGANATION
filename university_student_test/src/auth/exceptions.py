from auth.schemas.auth import UserCredentials
from fastapi import HTTPException, status
from functools import wraps
import httpx
import jwt


async def validate_user_credentials(credentials: UserCredentials) -> dict:
    username = credentials.username.strip()
    password = credentials.password.strip()

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Foydalanuvchi username yoki password yo'q",
        )

    try:
        login = int(username)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username son bo'lishi kerak",
        )

    return {"login": login, "password": password}


async def validate_token(token: str) -> str:
    if not token or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token bo'sh yoki mavjud emas (No token received from the authentication server).",
        )
    return token.strip()


def handle_httpx_errors(func):
    @wraps(func)  
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid login credentials",
                )
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Authentication server error: {e.response.text}",
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service is unavailable",
            )

    return wrapper


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def handle_jwt_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
    return wrapper

