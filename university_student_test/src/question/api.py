from fastapi import APIRouter , Depends , UploadFile , File
from sqlalchemy.ext.asyncio import AsyncSession

from .dtos import QuestionEnterDto , QuestionUpdateDto
from .service import QuestionService
from core.database.db_helper import db_helper
from auth.utils.security import require_permission 
from auth.schemas.auth import TokenPaylod


router = APIRouter(
    tags=["Questions"],
    prefix="/questions"
)

def get_question_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return QuestionService(session=session)

@router.post("/create")
async def create(
    question_data: QuestionEnterDto = Depends(),
    service: QuestionService = Depends(get_question_service),
    current_user: TokenPaylod = Depends(require_permission("create:questions"))
):
    return await service.create_question(question_data=question_data , teacher_id=current_user.user_id)


@router.post("/create/exel")
async def create_by_exel(
    subject_id: int,
    file: UploadFile = File(...),
    service: QuestionService = Depends(get_question_service),
    current_user: TokenPaylod = Depends(require_permission("create:questions")),
):
    return await service.create_question_by_exel(subject_id=subject_id, file=file , teacher_id=current_user.user_id)


@router.get("/get/{question_id}")
async def get_by_id(
    question_id: int,
    service: QuestionService = Depends(get_question_service),
    current_user: TokenPaylod = Depends(require_permission("read:questions")),
):
    return await service.get_question_by_id(question_id=question_id, teacher_id=current_user.user_id)


@router.get("")
async def get_all(
    limit: int = 20,
    offset: int = 0,
    service: QuestionService = Depends(get_question_service),
    current_user: TokenPaylod = Depends(require_permission("read:questions"))
):
    return await service.get_all_question(limit=limit , offset=offset , teacher_id=current_user.user_id)


@router.put("/update/{question_id}")
async def update(
    question_id: int,
    question_data: QuestionUpdateDto = Depends(),
    service: QuestionService = Depends(get_question_service),
    current_user: TokenPaylod = Depends(require_permission("update:questions")),
):
    return await service.update_question(question_id=question_id , question_data=question_data , teacher_id=current_user.user_id)


@router.delete("/delete/{question_id}")
async def delete(
    question_id: int,
    service: QuestionService = Depends(get_question_service),
    current_user: TokenPaylod = Depends(require_permission("delete:questions")),
):
    return await service.delete_question(question_id=question_id, teacher_id=current_user.user_id)

