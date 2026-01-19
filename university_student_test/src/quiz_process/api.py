from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import QuizProcessService
from .schemas import QuizSubmission
from core.database.db_helper import db_helper
from auth.schemas.auth import TokenPaylod
from auth.utils.security import require_permission

from core.logging import logging

router = APIRouter(
    tags=["Quiz Process"],
    prefix="/quiz_process"
)

logger = logging.getLogger(__name__)

def get_quiz_process_service(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> QuizProcessService:
    """Dependency to provide QuizProcessService."""
    return QuizProcessService(session=session)


@router.get("/start")
async def start_quiz(
    quiz_id: int,
    quiz_pin: str,
    group_id: int | None = None,
    service: QuizProcessService = Depends(get_quiz_process_service),
    current_user: TokenPaylod = Depends(require_permission("read:quiz_process")),
):
    logger.info(
        f"QUIZ_PROCESS_START | user={current_user.username} | "
        f"user_id={current_user.user_id} | quiz_id={quiz_id} | group_id={group_id}"
    )
    """Start a quiz for a user if it's active."""
    return await service.start_quiz(
        quiz_id=quiz_id,
        quiz_pin=quiz_pin,
        user_id=current_user.user_id,
        group_id=group_id,
    )


@router.post("/end")
async def end_quiz(
    submission: QuizSubmission,
    service: QuizProcessService = Depends(get_quiz_process_service),
    current_user: TokenPaylod = Depends(require_permission("create:quiz_process")),
):
    """Submit quiz answers and calculate results."""
    
    logger.info(
        f"QUIZ_PROCESS_END | user={current_user.username} | "
        f"user_id={current_user.user_id}"
    )
    return await service.end_quiz(
        submission=submission,
        student_id=current_user.user_id,
    )
