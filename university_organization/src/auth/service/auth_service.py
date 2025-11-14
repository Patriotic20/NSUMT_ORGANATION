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
        """
        Foydalanuvchini tizimga kirishini amalga oshiradi.

        Ushbu funksiya foydalanuvchini avvalo **mahalliy (local) ma'lumotlar bazasi** orqali
        tekshiradi. Agar foydalanuvchi topilmasa yoki parol noto‘g‘ri bo‘lsa, tizim foydalanuvchini
        **HEMIS** orqali autentifikatsiya qilishga harakat qiladi.

        Ish jarayoni quyidagicha amalga oshadi:
        1. `authenticate_user_from_db()` yordamida foydalanuvchini mahalliy bazadan qidiradi.
           - Agar foydalanuvchi topilsa va parol to‘g‘ri bo‘lsa → JWT tokenlar (access va refresh) yaratiladi.
        2. Agar foydalanuvchi topilmasa:
           - `authenticate_user_with_hemis()` orqali HEMIS tizimida foydalanuvchi ma'lumotlari tekshiriladi.
           - Agar HEMIS autentifikatsiya muvaffaqiyatli o‘tsa → foydalanuvchining ma'lumotlari
             `StudentService.save_student_data_to_db()` yordamida mahalliy bazaga saqlanadi.
        3. Saqlangandan so‘ng foydalanuvchi qaytadan bazadan olinadi (`authenticate_user_from_db` bilan)
           va unga yangi tokenlar yaratiladi.

        Xatolik holatlari:
        - 401 (UNAUTHORIZED): Login yoki parol noto‘g‘ri bo‘lsa.
        - 404 (NOT FOUND): HEMIS dan ma'lumot keldi, lekin foydalanuvchini bazada qayta topib bo‘lmasa.
        - 500 (INTERNAL SERVER ERROR): Bazaga saqlashda yoki kutilmagan xatolik yuz bersa.

        Parametrlar:
            credentials (UserCredentials): Foydalanuvchining login va paroli.

        Qaytaradi:
            dict: Quyidagi ma'lumotlarni o‘z ichiga oladi:
                - access_token: JWT access token
                - refresh_token: JWT refresh token
        """

        try:

            user_data: User | None = await authenticate_user_from_db(
                credentials=credentials,
                session=self.session
            )

            if user_data:
                roles = [role.name for role in user_data.roles]
                data = {
                    "user_id": user_data.id,
                    "username": user_data.username,
                    "role": roles
                }

                return {
                    "access_token": create_access_token(data=data),
                    "refresh_token": create_refresh_token(data=data),
                }
            
            try:

                token = await authenticate_user_with_hemis(
                    credentials=credentials,
                    session=self.session
                )
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Login yoki parol noto'g'ri"
                )
            
            try:
                service = StudentService(session=self.session, token=token)
                student_data = await service.save_student_data_to_db()
            except SQLAlchemyError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ma'lumotlar bazasi xatosi: {str(e)}"                
                    )
            user_data: User | None = await authenticate_user_from_db(
                credentials=credentials,
                session=self.session
            )

            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Foydalanuvchi ma'lumotlari topilmadi."
                )
            
            roles = [role.name for role in user_data.roles]
            data = {
                "user_id": user_data.id,
                "username": user_data.username,
                "group_id": getattr(user_data.student, "group_id", None),
                "role": roles,
            }

            return {
                "access_token": create_access_token(data=data),
                "refresh_token": create_refresh_token(data=data),
            }
        
        except HTTPException:
            raise  # Let FastAPI handle HTTP exceptions
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Kutilmagan xato: {str(e)}"
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
