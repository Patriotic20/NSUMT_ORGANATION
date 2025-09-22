from pydantic import BaseModel, field_validator , Field
from core.utils.normalize_type_name import normalize_type_name


class WorkerBase(BaseModel):
    
    department_id: int
    first_name: str
    last_name: str
    patronymic: str

    @field_validator("first_name", "last_name", "patronymic")
    @classmethod
    def normalize(cls, value: str) -> str:
        return normalize_type_name(value)


class WorkerCreate(WorkerBase):
    user_id: int



class WorkerResponse(WorkerCreate):
    id: int


class WorkerUpdate(BaseModel):
    
    department_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None

    @field_validator("first_name", "last_name", "patronymic")
    @classmethod
    def normalize(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return normalize_type_name(value)

class WorkerGet(BaseModel):
    id: int = Field(..., description="Worker ID")
    user_id: int | None = Field(None, description="Related user ID")
    department_id: int | None = Field(None, description="Related department ID")
