from pydantic import BaseModel, field_validator, Field, field_serializer, ConfigDict
from datetime import datetime
from fastapi import HTTPException, status


DEFAULT_START_TIME = datetime(1970, 1, 1, 0, 0, 0)


class QuizBase(BaseModel):
    subject_id: int
    question_number: int
    quiz_time: int
    start_time: datetime = Field(default=DEFAULT_START_TIME)
    quiz_pin: str

    @field_validator("start_time", mode="before")
    def normalize_start_time(cls, v) -> datetime:
        """
        Convert input to naive datetime, strip seconds/microseconds,
        and ensure it's not in the past.
        """
        # Convert from string if needed
        if isinstance(v, str):
            v = datetime.fromisoformat(v)

        if not isinstance(v, datetime):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_time must be a valid datetime"
            )

        # Make naive and round to minute
        v = v.replace(second=0, microsecond=0)

        # Check not in the past
        now = datetime.now().replace(second=0, microsecond=0)
        if v < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time cannot be in the past"
            )
        return v


class QuizCreate(QuizBase):
    teacher_id: int


class QuizResponse(QuizCreate):
    id: int
    subject_id: int
    teacher_id: int | None = None
    question_number: int
    quiz_time: int
    start_time: datetime
    end_time: datetime
    quiz_pin: str

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("start_time", "end_time", when_used="json")
    def serialize_dt(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")


class QuizUpdate(BaseModel):
    question_number: int | None = None
    quiz_time: int | None = None
    start_time: datetime = Field(default=DEFAULT_START_TIME)
    quiz_pin: str | None = None

    @field_validator("start_time", mode="before")
    def normalize_start_time(cls, v) -> datetime:
        # If sentinel default, do not change
        if v == DEFAULT_START_TIME:
            return v

        if isinstance(v, str):
            v = datetime.fromisoformat(v)

        if not isinstance(v, datetime):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_time must be a valid datetime"
            )

        # Make naive and round to minute
        v = v.replace(second=0, microsecond=0)

        # Check not in the past
        now = datetime.now().replace(second=0, microsecond=0)
        if v < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time cannot be in the past"
            )
        return v
