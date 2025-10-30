from fastapi import APIRouter , Depends , UploadFile , File
from sqlalchemy.ext.asyncio import AsyncSession

from .service import QuestionService, QuestionUpdate
from core.database.db_helper import db_helper
from auth.utils.security import require_permission 
from auth.schemas.auth import TokenPaylod
from .schemas import QuestionCreate


router = APIRouter(
    tags=["Questions"],
    prefix="/questions"
)

def get_question_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return QuestionService(session=session)

@router.post("/create")
async def create(
    question_data: QuestionCreate,
    service: QuestionService = Depends(get_question_service),
    _ : TokenPaylod = Depends(require_permission("create:questions"))
):
    return await service.create_question(question_data=question_data)


@router.post("/create/exel")
async def create_by_exel(
    subject_id: int,
    file: UploadFile = File(...),
    service: QuestionService = Depends(get_question_service),
    _ : TokenPaylod = Depends(require_permission("create:questions")),
):
    return await service.create_question_by_exel(subject_id=subject_id, file=file)


@router.get("/get/{question_id}")
async def get_by_id(
    question_id: int,
    service: QuestionService = Depends(get_question_service),
    _ : TokenPaylod = Depends(require_permission("read:questions")),
):
    return await service.get_question_by_id(question_id = question_id)


@router.get("")
async def get_all(
    limit: int = 20,
    offset: int = 0,
    service: QuestionService = Depends(get_question_service),
    _ : TokenPaylod = Depends(require_permission("read:questions"))
):
    return await service.get_all_question(limit=limit , offset=offset)


@router.put("/update/{question_id}")
async def update(
    question_id: int,
    question_data: QuestionUpdate  ,
    service: QuestionService = Depends(get_question_service),
    _ : TokenPaylod = Depends(require_permission("update:questions")),
):
    return await service.update_question(question_id=question_id , question_data=question_data)


@router.delete("/delete/{question_id}")
async def delete(
    question_id: int,
    service: QuestionService = Depends(get_question_service),
    _ : TokenPaylod = Depends(require_permission("delete:questions")),
):
    return await service.delete_question(question_id=question_id)

