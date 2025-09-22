from pydantic import BaseModel , Field, field_validator
from datetime import date
from core.utils.normalize_type_name import normalize_type_name

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
    
    
    @field_validator("*", mode="before")
    @classmethod
    def normalize_strings(cls, v):
        if isinstance(v, str):
            return normalize_type_name(v)
        return v


class StudentCreate(StudentBase):
    
    user_id: int
    group_id: int


class StudentResponse(StudentBase):
    id: int
    group_id: int
    user_id: int

class StudentGet(BaseModel):
    
    id: int = Field(..., description="Unique ID of the student")
    user_id: int| None = Field(None, description="Associated user ID")
    group_id: int| None = Field(None, description="ID of the group the student belongs to")

