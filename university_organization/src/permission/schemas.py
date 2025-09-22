from pydantic import BaseModel, field_validator

class PermissionBase(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def normalize_value(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("name cannot be empty")
        return value.strip().lower()


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_value(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("name cannot be empty")
        return value.strip().lower()


class PermissionResponse(PermissionBase):
    
    id: int
