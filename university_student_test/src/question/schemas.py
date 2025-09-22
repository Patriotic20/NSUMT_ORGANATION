from pydantic import BaseModel



class QuestionBase(BaseModel):
    text: str
    image: str | None = None
    option_a: str | None = None
    option_a_image: str | None = None
    option_b: str | None = None
    option_b_image: str | None = None
    option_c: str | None = None
    option_c_image: str | None = None
    option_d: str | None = None
    option_d_image: str | None = None


class QuestionCreate(QuestionBase):
    
    subject_id: int


class QuestionResponse(QuestionCreate):
    id: int


class QuestionUpdate(BaseModel):
    text: str | None = None
    image: str | None = None
    option_a: str | None = None
    option_a_image: str | None = None
    option_b: str | None = None
    option_b_image: str | None = None
    option_c: str | None = None
    option_c_image: str | None = None
    option_d: str | None = None
    option_d_image: str | None = None
