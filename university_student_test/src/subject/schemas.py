from pydantic import BaseModel

class SubjectBase(BaseModel):
    name: str

class SubjectCreate(SubjectBase):
    
    teacher_id: int
    


class SubjectResponse(SubjectBase):
    id: int
    
    
class SubjectUpdate(BaseModel):
    name: str | None = None
