from jwt.exceptions import InvalidTokenError
import jwt

from core.config import settings
from core.utils.database import db_helper
from core.models.user import User
from utils import get_user

from schemas import TokenPaylod

from faststream import FastStream
from faststream.rabbit import RabbitBroker
import asyncio

from core.config import settings

broker = RabbitBroker(settings.rabbit.url)
app = FastStream(broker)


@broker.subscriber(settings.rabbit.queue_name)
async def validate_token_subscriber(token: str) -> TokenPaylod:
    try:
        payload = jwt.decode(
            token,
            settings.jwt.access_secret_key,
            algorithms=[settings.jwt.algorithm],
        )
        username = payload.get("username")
        if not username:
            return TokenPaylod(valid=False)
    except InvalidTokenError:
        return TokenPaylod(valid=False)

    async with db_helper.session_factory() as session:
        user: User | None = await get_user(session, username=username)
        if not user:
            return TokenPaylod(valid=False)

    return TokenPaylod(
        valid=True,
        user_id=user.id,
        group_id=payload.get("group_id"),
        username=user.username,
        role=user.roles[0].name if user.roles else None,
        permissions=[p.name for r in user.roles for p in r.permissions],
    )


if __name__ == "__main__":
    asyncio.run(app.run())
