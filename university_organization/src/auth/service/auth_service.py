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

from sqlalchemy.exc import SQLAlchemyError


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def login(self, credentials: UserCredentials):
        try:
            # Try to authenticate locally first
            user_data: User = await authenticate_user_from_db(
                credentials=credentials, 
                session=self.session
            )

            if user_data:
                # Existing user found
                roles = [role.name for role in user_data.roles]
                data = {
                    "user_id": user_data.id,
                    "username": user_data.username,
                    "role": roles,
                }

            else:
                # Try to authenticate with HEMIS if user not found locally
                try:
                    token = await authenticate_user_with_hemis(
                        credentials=credentials, 
                        session=self.session
                    )
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Failed to authenticate with HEMIS: {str(e)}"
                    )

                # Save student data from HEMIS
                try:
                    service = StudentService(session=self.session, token=token)
                    student_data = await service.save_student_data_to_db()
                except SQLAlchemyError as e:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Database error while saving student data: {str(e)}"
                    )

                # Re-fetch the user after saving new data
                user_data: User = await authenticate_user_from_db(
                    credentials=credentials, 
                    session=self.session
                )

                if not user_data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User data could not be retrieved after saving."
                    )

                roles = [role.name for role in user_data.roles]
                data = {
                    "user_id": student_data["user_id"],
                    "username": student_data["username"],
                    "group_id": student_data.get("group_id"),
                    "role": roles,
                }

            return {
                "access_token": create_access_token(data=data),
                "refresh_token": create_refresh_token(data=data),
            }

        except SQLAlchemyError as e:
            # General database exception
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

        except HTTPException:
            # Re-raise HTTPExceptions we created above
            raise

        except Exception as e:
            # Catch-all for unexpected errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error during login: {str(e)}"
            )




    async def register(self, credentials: UserCredentials):
        hashed_password = hash_password(password=credentials.password)
        credentials_with_hash = UserCredentials(
            username=credentials.username,
            password=hashed_password,
        )
        
        
        user_data = await BasicService(session=self.session).create(
            model=User, 
            create_data=credentials_with_hash, 
            filters=[User.username == credentials_with_hash.username]
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
