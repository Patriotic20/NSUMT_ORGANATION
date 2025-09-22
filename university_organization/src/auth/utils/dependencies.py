from faststream.rabbit import RabbitBroker
from fastapi import HTTPException , status, Depends
from typing import Annotated , Callable

from auth.schemas.auth import TokenPaylod
from auth.utils.security import oauth2_scheme



async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> TokenPaylod:
    async with RabbitBroker("amqp://guest:guest@localhost:5672/") as broker:
        response = await broker.publish(
            token,
            "auth.validate_token",
            rpc=True,
            rpc_timeout=5,
        )

    payload = TokenPaylod(**response)

    if not payload.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return payload

def require_permission(*permissions: str, any_of: bool = True) -> Callable:
    async def checker(user: TokenPaylod = Depends(get_current_user)) -> TokenPaylod:
        user_perms = set(user.permissions)

        if any_of:
            if not any(p in user_perms for p in permissions):
                raise HTTPException(status_code=403, detail="Permission denied")
        else:
            if not all(p in user_perms for p in permissions):
                raise HTTPException(status_code=403, detail="Permission denied")

        return user

    return checker
