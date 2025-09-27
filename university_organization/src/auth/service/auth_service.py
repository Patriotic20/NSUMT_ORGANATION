from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  HTTPException , status
import jwt

from core.models import User 
from core.utils.service import BasicService
from core.config import settings
from core.models import User

from auth.schemas.auth import UserCredentials 
from auth.utils.authenticate import authenticate_user_with_hemis, authenticate_user_from_db
from auth.service.student_service import StudentService
from auth.utils.security import create_access_token, create_refresh_token, hash_password 
from auth.exceptions import handle_jwt_exceptions




class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def login(self, credentials: UserCredentials):
        user_data: User = await authenticate_user_from_db(
            credentials=credentials, session=self.session
        )
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The authentication service did not find the user data"
            )
        
        if user_data:
            
            data = {
                "user_id": user_data.id,       
                "username": user_data.username,
            }
        else:
        
            token = await authenticate_user_with_hemis(
                credentials=credentials, session=self.session
            )
            service = StudentService(db=self.session, token=token)
            student_data = await service.save_student_data_to_db()

            data = {
                "user_id": student_data.id,
                "username": student_data.username,                 
            }

        return {
            "access_token": create_access_token(data=data),
            "refresh_token": create_refresh_token(data=data),
        }



    async def register(self, credentials: UserCredentials):
        hashed_password = hash_password(password=credentials.password)
        credentials_with_hash = UserCredentials(
            username=credentials.username,
            password=hashed_password,
        )

        user_data = await BasicService(session=self.session).create(
            model=User, create_data=credentials_with_hash
        )
        return user_data

    @handle_jwt_exceptions
    async def refresh(self, refresh_token: str):
        payload = jwt.decode(
            refresh_token,
            settings.jwt.refresh_secret_key,
            algorithms=[settings.jwt.algorithm],
        )

        username = payload.get("username")
        role = payload.get("role")

        if not username or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        access_token = create_access_token(data={"username": username, "role": role})
        return {"access_token": access_token, "token_type": "bearer"}
