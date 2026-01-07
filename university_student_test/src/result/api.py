from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.db_helper import db_helper

from auth.schemas.auth import TokenPaylod
from auth.utils.security import require_permission
from .service import ResultService

router = APIRouter(
    tags=["Result"],
    prefix="/result",
)


def get_service(session: AsyncSession = Depends(db_helper.session_getter)) -> ResultService:
    """Dependency to provide ResultService instance."""
    return ResultService(session=session)

@router.get("/user_answers/{user_id}")
async def user_answers(
    user_id: int,
    service: ResultService = Depends(get_service),
    _ : TokenPaylod = Depends(require_permission("read:result")),
):
    return await service.get_users_answers(user_id=user_id)

@router.get("/get/{result_id}")
async def get_by_id(
    result_id: int,
    service: ResultService = Depends(get_service),
    current_user: TokenPaylod = Depends(require_permission("read:result")),
):
    """Retrieve a result by its ID."""
    return await service.get_by_id(
        id=result_id,
        user_id=current_user.user_id,
        is_admin=current_user.role,
    )


@router.get("/get_by_filed")
async def get_by_filed(
    quiz_id: int | None = None,
    service: ResultService = Depends(get_service),
    current_user: TokenPaylod = Depends(require_permission("read:result")),
):
    """
    Retrieve results grouped by student and filtered by given fields.
    """
    return await service.get_by_field(
        quiz_id=quiz_id,
    )


@router.get("/get_by_username")
async def get_by_username(
    username: str,
    desc: bool,
    service: ResultService = Depends(get_service),
    current_user: TokenPaylod = Depends(require_permission("read:result")),
):
    return await service.get_by_username(
        username=username,
        desc=desc,
    )

@router.get("")
async def get_all(
    limit: int = 20,
    offset: int = 0,
    service: ResultService = Depends(get_service),
    current_user: TokenPaylod = Depends(require_permission("read:result")),
):
    """Retrieve all results with pagination."""
    return await service.get_all(
        user_id=current_user.user_id,
        is_admin=current_user.role,
        limit=limit,
        offset=offset,
    )


@router.delete("/delete/{result_id}")
async def delete(
    result_id: int,
    service: ResultService = Depends(get_service),
    current_user: TokenPaylod = Depends(require_permission("delete:result")),
):
    """Delete a result by ID."""
    return await service.delete(
        id=result_id,
        user_id=current_user.user_id,
        is_admin=current_user.role,
    )
