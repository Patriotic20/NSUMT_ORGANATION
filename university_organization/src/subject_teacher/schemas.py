from pydantic import BaseModel


class SubjectTeacherCreate(BaseModel):
    
    subject_id: int
    teacher_id: int


class SubjectTeacherCreate(BaseModel):
    
    subject_id: int | None = None
    teacher_id: int | None = None 
