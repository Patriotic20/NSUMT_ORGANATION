from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    role_name: str
    
    
class UserResponse(UserBase):
    id: int
    
class UserRoleCreate(BaseModel):
    role_id: int
    user_id: int


class WorkerResponse(BaseModel):
    id: int
    department_id: int
    first_name: str
    last_name: str
    patronymic: str

class StudentResponse(BaseModel):
    id: int
    department_id: int
    first_name: str
    last_name: str
    patronymic: str

class TeacherResponse(BaseModel):
    id: int
    department_id: int
    first_name: str
    last_name: str
    patronymic: str

class UserResponse(BaseModel):
    id: int
    username: str
    roles: list[str]
    worker: Optional[WorkerResponse] = None
    student: Optional[StudentResponse] = None
    teacher: Optional[TeacherResponse] = None
