from pydantic import BaseModel, Field, field_validator
# from core.utils.normalize_type_name import normalize_type_name


class TeacherBase(BaseModel):
    user_id: int
    chair_id: int
    first_name: str
    last_name: str
    patronymic: str

    # Normalize name fields before validation
    # @field_validator(
    #     "first_name",
    #     "last_name",
    #     "patronymic",
    #     mode="before"
    # )
    # @classmethod
    # def normalizing(cls, value: str) -> str:
    #     return normalize_type_name(value)


class TeacherUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None

    # @field_validator("*", mode="before")
    # @classmethod
    # def normalizing(cls, value: str) -> str:
    #     # Skip None values
    #     if value is None:
    #         return value
    #     return normalize_type_name(value)


class TeacherResponse(TeacherBase):
    id: int


class TeacherGet(BaseModel):
    teacher_id: int = Field(..., gt=0, description="ID of the user, must be greater than 0")
