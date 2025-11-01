from pydantic import BaseModel


class GroupTeacherCreate(BaseModel):
    group_id: int
    teacher_id: int
    


class GroupTeacherUpdate(BaseModel):
    group_id: int | None = None
    teacher_id: int | None = None

