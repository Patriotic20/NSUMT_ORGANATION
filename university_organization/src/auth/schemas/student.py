from pydantic import BaseModel
from datetime import date


class StudentBase(BaseModel):
    
    first_name: str | None = None
    last_name: str | None = None
    third_name: str | None = None
    full_name: str | None = None
    student_id_number: str | None = None
    image_path: str | None = None
    birth_date: date | None = None
    passport_pin: str | None = None
    passport_number: str | None = None
    phone: str | None = None
    gender: str | None = None
    university: str | None = None
    specialty: str | None = None
    student_status: str | None = None
    education_form: str | None = None
    education_type: str | None = None
    payment_form: str | None = None
    education_lang: str | None = None
    faculty: str | None = None
    level: str | None = None
    semester: str | None = None
    address: str | None = None
    avg_gpa: float | None = None


class StudentCreate(StudentBase):
    
    user_id: int
    group_id: int


class StudentResponse(StudentBase):
    id: int
    user_id: int
