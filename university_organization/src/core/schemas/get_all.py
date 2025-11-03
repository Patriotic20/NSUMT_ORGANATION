from pydantic import BaseModel, Field

class GetAll(BaseModel):
    
    limit: int = Field(default=20, le=500, ge=1, description="Number of items to return (max 500)")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
