from pydantic import BaseModel

class RolePermissionCreate(BaseModel):
    
    role_id: int
    permission_id: int
    
    
class RolePermissionUpdate(BaseModel):
    
    role_id: int | None = None 
    permission_id: int | None = None
