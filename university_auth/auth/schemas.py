from pydantic import BaseModel, Field

class TokenPaylod(BaseModel):
    valid: bool
    user_id: int | None = None
    username: str | None = None
    role: str | None = None
    permissions: list[str] = Field(default_factory=list)
