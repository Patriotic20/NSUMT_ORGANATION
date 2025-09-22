from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import QuizProcessService
from .schemas import QuizSubmission

from core.database.db_helper import db_helper

from auth.schemas.auth import TokenPaylod
from auth.utils.security import require_permission





router = APIRouter(
    tags=["Quiz Process"],
    prefix="/quiz_process"
)

def get_quiz_process_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return QuizProcessService(session=session)



@router.get('/get/test')
async def get_test(
    quiz_id: int,
    quiz_pin: str,
    service: QuizProcessService = Depends(get_quiz_process_service),
    current_user: TokenPaylod = Depends(require_permission("read:quiz_process"))
):
    return await service.create_questions(quiz_id=quiz_id, quiz_pin=quiz_pin)


@router.post("/test_results")
async def check_result(
    questions: QuizSubmission,
    service: QuizProcessService = Depends(get_quiz_process_service),
    current_user: TokenPaylod = Depends(require_permission("create:quiz_process"))
):
    return await service.take_questions(submitted_questions=questions, student_id=current_user.user_id)
