from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from .security import get_user , verify_password

from core.config import settings

from auth.exceptions import validate_user_credentials , validate_token , handle_httpx_errors
from auth.utils.register_user import student_register
from auth.schemas.auth import UserCredentials

@handle_httpx_errors
async def authenticate_user_with_hemis(
    credentials: UserCredentials,
    session: AsyncSession
):

    payload = await validate_user_credentials(credentials=credentials)

    url = f"{settings.hemis.base_url}/auth/login"
    headers = {"Content-Type": "application/json"}

    async with AsyncClient() as client:
        response = await client.post(url=url, json=payload, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        token = response_data.get("data", {}).get("token")


    validated_token = await validate_token(token=token)
    
    await student_register(session=session , credentials=credentials)

    return validated_token


        
async def authenticate_user_from_db(
    credentials: UserCredentials,
    session: AsyncSession
):
    user_data = await get_user(
        session=session, 
        username=credentials.username
        )
    
    if not user_data:
        return False
    
    if not verify_password(plain_password=credentials.password , hashed_password=user_data.password):
        return False
    
    return user_data
    
