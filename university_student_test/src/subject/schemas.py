from pydantic import BaseModel

class SubjectBase(BaseModel):
    name: str

class SubjectCreate(SubjectBase):
    
    teacher_id: int | None = None
    


class SubjectResponse(SubjectBase):
    id: int
    
    
class SubjectUpdate(BaseModel):
    teacher_id: int | None = None
    name: str | None = None
