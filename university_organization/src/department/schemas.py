from pydantic import BaseModel, field_validator
from core.utils.normalize_type_name import normalize_type_name


class DepartmentBase(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def normalize(cls, value: str) -> str: 
        return normalize_type_name(value)


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: int


class DepartmentUpdate(BaseModel):
    name: str | None = None

    @field_validator("name")
    @classmethod
    def normalize(cls, value: str | None) -> str | None: 
        if value is None:
            return value
        return normalize_type_name(value)

