from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import select 



from auth.schemas.student import StudentCreate
from auth.utils.request_hemis import fetch_hemis_data
from auth.utils.security import get_user
from core.config import settings
from core.models import Student, User, Group
from core.utils.service import BasicService
from auth.utils.faculty_group import group_create_check
from core.utils.normalize_type_name import normalize_type_name


class StudentService:
    def __init__(self, session: AsyncSession, token: str):
        self.session = session
        self.token = token

    async def fetch_student_data(self):
        return await fetch_hemis_data(
            base_url=settings.hemis.base_url, endpoint="account/me", token=self.token
        )

    async def map_student_data(self):
        api_data = await self.fetch_student_data()
        user_data = {
            "first_name": api_data.get("first_name"),
            "last_name": api_data.get("second_name"),
            "third_name": api_data.get("third_name"),
            "full_name": api_data.get("full_name"),
            "student_id_number": api_data.get("student_id_number"),
            "image_path": api_data.get("image"),
            "birth_date": api_data.get("birth_date"),
            "passport_pin": api_data.get("passport_pin"),
            "passport_number": api_data.get("passport_number"),
            "phone": api_data.get("phone"),
            "gender": api_data.get("gender", {}).get("name"),
            "university": api_data.get("university"),
            "specialty": api_data.get("specialty", {}).get("name"),
            "student_status": api_data.get("studentStatus", {}).get("name"),
            "education_form": api_data.get("educationForm", {}).get("name"),
            "education_type": api_data.get("educationType", {}).get("name"),
            "payment_form": api_data.get("paymentForm", {}).get("name"),
            "group": api_data.get("group", {}).get("name"),
            "education_lang": api_data.get("educationLang", {}).get("name"),
            "faculty": api_data.get("faculty", {}).get("name"),
            "level": api_data.get("level", {}).get("name"),
            "semester": api_data.get("semester", {}).get("name"),
            "address": api_data.get("address"),
            "avg_gpa": api_data.get("avg_gpa"),
        }

        if user_data["birth_date"]:
            try:
                user_data["birth_date"] = datetime.fromtimestamp(
                    user_data["birth_date"]
                ).date()
            except (TypeError, ValueError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="birth_date is invalid in API response",
                )

        OPTIONAL_FIELDS = {"passport_pin", "passport_number"}
        missing_fields = [
            key
            for key, value in user_data.items()
            if value is None and key not in OPTIONAL_FIELDS
        ]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Required fields missing in API response: {', '.join(missing_fields)}",
            )

        return user_data
    
        
    async def save_student_data_to_db(self):
        student_data = await self.map_student_data()
        username = student_data.get("student_id_number")
        group_name = student_data.get("group")
        faculty_name = student_data.get("faculty")

        # Get user
        user_data: User = await get_user(session=self.session, username=username)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with username '{username}' not found"
            )

        # Ensure group exists or create it
        group_data = await group_create_check(
            group_name=group_name,
            faculty_name=faculty_name,
            session=self.session
        )

        # Prepare schema and create student
        student_schema = StudentCreate(
            group_id=group_data.id,
            user_id=user_data.id,
            **student_data
        )

        await BasicService(session=self.session).create(
            model=Student,
            create_data=student_schema,
        )

        # Return only required fields
        return {
            "user_id": user_data.id,
            "group_id": group_data.id,
            "username": username
        }

