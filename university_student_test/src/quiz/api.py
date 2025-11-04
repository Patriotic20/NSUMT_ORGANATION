from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from .service import QuizService 
from .schemas import QuizBase, QuizUpdate, QuizCreate

from core.database.db_helper import db_helper 
from auth.schemas.auth import TokenPaylod
from auth.utils.security import require_permission
from core.utils.save_file import save_file

router = APIRouter(
    tags=["Quiz"],
    prefix="/quiz"
)

def get_quiz_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return QuizService(session=session)


@router.post("/create")
async def create(
    quiz_data: QuizBase,
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("create:quiz"))
):
    quiz_create = QuizCreate(
        user_id=current_user.user_id,
        **quiz_data.model_dump()
    )
    return await service.create_quiz(quiz_data=quiz_create)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    url_data = save_file(file=file)
    return {"file_url": url_data}


@router.get("/get/{quiz_id}")
async def get_by_id(
    quiz_id: int,
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("read:quiz"))
):
    role = current_user.role[0] if current_user.role else None
    return await service.get_quiz_by_id(
        quiz_id=quiz_id,
        user_id=current_user.user_id,
        is_admin=role
    )


@router.get("")
async def get_all(
    limit: int = 20,
    offset: int = 0,
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("read:quiz"))
):
    role = current_user.role[0] if current_user.role else None
    return await service.get_all_quiz(
        user_id=current_user.user_id,
        is_admin=role,
        limit=limit,
        offset=offset,
        group_id=current_user.group_id
    )


@router.patch("/update/{quiz_id}")
async def update(
    quiz_id: int,
    quiz_data: QuizUpdate,
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("update:quiz"))
):
    role = current_user.role[0] if current_user.role else None
    return await service.update_quiz(
        quiz_id=quiz_id,
        user_id=current_user.user_id,
        quiz_data=quiz_data,
        is_admin=role
    )


@router.delete("/delete/{quiz_id}")
async def delete(
    quiz_id: int,
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("delete:quiz"))
):
    role = current_user.role[0] if current_user.role else None
    await service.delete_quiz(
        quiz_id=quiz_id,
        user_id=current_user.user_id,
        is_admin=role
    )
    return {"message": "Deleted successfully"}
