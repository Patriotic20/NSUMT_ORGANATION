from pydantic import BaseModel, field_validator
from core.utils.normalize_type_name import normalize_type_name


class FacultyBase(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def normalize(cls, value: str) -> str:
        return normalize_type_name(value)


class FacultyCreate(FacultyBase):
    pass


class FacultyUpdate(BaseModel):
    name: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        
        return normalize_type_name(value)


class FacultyResponse(BaseModel):
    
    id: int
    name: str
