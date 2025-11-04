from pydantic import BaseModel, field_validator , Field
from fastapi import Query


class LoginDto:
    def __init__(
        self, 
        username: str = Query(...), 
        password: str = Query(...),

        
        ):
        
        self.username = username
        self.password = password
 
        
        
class RefreshToken:
    def __init__(
        self, 
        refresh_token: str = Query(...)
        ):
        
        self.refresh_token = refresh_token


class UserCredentials(BaseModel):
    username: str
    password: str
    role_id: int

    @field_validator("username", "password")
    @classmethod
    def strip_and_validate_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Bo'sh qiymatga ruxsat berilmaydi (Empty values are not allowed)")
        return value


class UserRequest(BaseModel):
    username: str
    password: str
    
    @field_validator("username", "password")
    @classmethod
    def strip_and_validate_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Bo'sh qiymatga ruxsat berilmaydi (Empty values are not allowed)")
        return value

class RoleBase(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip().lower()



class TokenPaylod(BaseModel):
    valid: bool
    user_id: int | None = None
    group_id: int | None = None
    username: str | None = None
    role: str | None = None
    permissions: list[str] = Field(default_factory=list)
