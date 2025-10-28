from pydantic import BaseModel , Field, field_validator
from core.utils.normalize_type_name import normalize_type_name

class TeacherBase(BaseModel):
    
    chair_id: int
    first_name: str
    last_name: str
    patronymic: str
    
    @field_validator(
        "first_name", 
        "last_name", 
        "patronymic",
        mode="before",)
    @classmethod
    def normalizing(cls, value: str) -> str:
        if isinstance(str, value):
            return normalize_type_name(value)
        return value


class TeacherCreate(TeacherBase):
    
    user_id: int
    
    
class TeacherUpdate(BaseModel):
    
    first_name: str  | None = None
    last_name: str | None = None
    patronymic: str | None = None
    
    
    @field_validator("*", mode="before")
    @classmethod
    def normalizing(cls, value: str) -> str:
        if isinstance(str, value):
            return normalize_type_name(value)
        return value
    
class TeacherResponse(TeacherCreate):
    
    id: int
    
    
class TeacherGet(BaseModel):
    
    id: int = Field(..., gt=0, description="Unique identifier of the teacher, must be greater than 0")
    user_id: int = Field(..., gt=0, description="ID of the user, must be greater than 0")
    chair_id: int | None = Field(None, description="Optional chair ID associated with the teacher")
