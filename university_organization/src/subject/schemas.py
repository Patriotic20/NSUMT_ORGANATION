from pydantic import BaseModel

class SubjectBase(BaseModel):
    name: str
    
class AssignTeacher(BaseModel):
    subject_id: int
    teacher_id: int


class SubjectResponse(SubjectBase):
    id: int
    
    
class SubjectUpdate(BaseModel):
    name: str | None = None
