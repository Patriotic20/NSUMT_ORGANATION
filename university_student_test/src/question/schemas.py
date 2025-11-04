from pydantic import BaseModel



class QuestionBase(BaseModel):
    subject_id: int
    text: str
    option_a: str | None = None
    option_b: str | None = None
    option_c: str | None = None
    option_d: str | None = None


class QuestionCreate(QuestionBase):
    user_id: int

    


class QuestionResponse(QuestionCreate):
    id: int


class QuestionUpdate(BaseModel):
    text: str | None = None
    option_a: str | None = None
    option_b: str | None = None
    option_c: str | None = None
    option_d: str | None = None
