from pydantic import BaseModel, field_validator , Field
from core.utils.normalize_type_name import normalize_type_name
from typing import Optional


class ChairBase(BaseModel):
    name: str

    @field_validator("name")   
    @classmethod
    def normalize(cls, value: str) -> str:
        return normalize_type_name(value)


class ChairCreate(ChairBase):
    faculty_id: int


class ChairGet(BaseModel):
    id: int = Field(..., description="Unique identifier of the chair")
    faculty_id: Optional[int] = Field(None, description="Related faculty ID")


class ChairUpdate(BaseModel):
    name: str | None = None

    @field_validator("name")
    @classmethod
    def normalize(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return normalize_type_name(value)


class ChairResponse(ChairCreate):
    id: int

