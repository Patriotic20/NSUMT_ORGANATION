from typing import Annotated
from fastapi import Depends , HTTPException , status
from fastapi.security import OAuth2PasswordBearer
import jwt
from core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: Annotated[str ,Depends(oauth2_scheme)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = jwt.decode(token , settings.jwt.access_secret_key, algorithms=[settings.jwt.algorithm])
    
    user_id: int = payload.get("user_id")
    role: str = payload.get("role")
    group_name: str = payload.get("group")
    
        
        
