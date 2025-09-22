from pydantic import BaseModel , Field

class RoleBase(BaseModel):
    
    name: str
    
    
class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    
    name: str | None = None
    
    
class RoleResponse(RoleBase):
    
    id: int

class RolePermission(BaseModel):
    
    role_id: int = Field(...)
    permission_id: int = Field(...)
