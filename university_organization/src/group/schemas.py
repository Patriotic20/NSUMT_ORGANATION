from pydantic import BaseModel, field_validator , Field
from core.utils.normalize_type_name import normalize_type_name

class GroupBase(BaseModel):
    
    name: str 
    
    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return normalize_type_name(v)
    
    
class GroupCreate(GroupBase):
    
    faculty_id: int
    

class GroupResponse(GroupCreate):
    
    id: int
    
    

class GroupUpdate(BaseModel):
    
    name: str | None = None
    
    
    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return normalize_type_name(v)


class GroupGet(BaseModel):
    
    id: int = Field(..., gt=0, description="Unique identifier of the group, must be > 0")
    faculty_id: int | None = Field(None, description="Optional faculty ID associated with the group")


class AssignData(BaseModel):
    group_id: int
    teacher_id: int
