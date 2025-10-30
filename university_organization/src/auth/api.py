from fastapi import APIRouter , Depends
from sqlalchemy.ext.asyncio import AsyncSession


from .schemas.auth import (
    UserCredentials,
    RefreshToken,
    LoginRequest
)
from .service.auth_service import AuthService
from core.utils.database import db_helper


router = APIRouter(
    tags=["Auth"],
    prefix="/auth"
)

def get_auth_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return AuthService(session=session)

@router.post("/register")
async def register(
    register_data: UserCredentials,
    service: AuthService = Depends(get_auth_service)
):
    user_data = await service.register(credentials=register_data)
    return {"id": user_data.id}

@router.post("/login")
async def login(
    login_data: LoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    return await service.login(credentials=login_data)

@router.post("/refresh")
async def refresh_token(
    refresh_token: RefreshToken = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    return service.refresh(refresh_token=refresh_token)
