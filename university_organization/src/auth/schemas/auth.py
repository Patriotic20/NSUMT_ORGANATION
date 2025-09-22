from pydantic import BaseModel, field_validator , Field
from fastapi import HTTPException, status


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=128)


class RefreshToken(BaseModel):
    refresh_token: str = Field(..., min_length=10)
        
        
class UserCredentials(BaseModel):
    username: str 
    password: str 

    @field_validator("username", "password")
    @classmethod
    def strip_and_validate_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=("Bo'sh qiymatga ruxsat berilmaydi (Empty values are not allowed)")
            )
        return value



class RoleBase(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip().lower()


class UserRoleCreate(BaseModel):
    user_id: int
    role_id: int

class TokenPaylod(BaseModel):
    valid: bool
    user_id: int | None = None
    username: str | None = None
    permissions: list[str] = Field(default_factory=list)
