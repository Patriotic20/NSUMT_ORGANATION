from fastapi import APIRouter , Depends , UploadFile , File
from sqlalchemy.ext.asyncio import AsyncSession

from .service import QuestionService, QuestionUpdate , QuestionBase
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
    question_data: QuestionBase,
    service: QuestionService = Depends(get_question_service),
    current_user: TokenPaylod = Depends(require_permission("create:questions")),
):
    create_data = QuestionCreate(
        user_id=current_user.user_id,
        **question_data.model_dump()
    )
    return await service.create_question(question_data=create_data)



@router.post("/create/exel")
async def create_by_exel(
    subject_id: int,
    file: UploadFile = File(...),
    service: QuestionService = Depends(get_question_service),
    current_user: TokenPaylod = Depends(require_permission("create:questions")),
):
    return await service.create_question_by_exel(
        subject_id=subject_id,
        file=file,
        user_id=current_user.user_id
    )



@router.get("/get/{question_id}")
async def get_by_id(
    question_id: int,
    service: QuestionService = Depends(get_question_service),
    current_user: TokenPaylod = Depends(require_permission("read:questions")),
):
    role = current_user.roles[0] if current_user.roles else None

    return await service.get_question_by_id(
        question_id=question_id,
        user_id=current_user.user_id,
        role=role
    )



@router.get("")
async def get_all(
    limit: int = 20,
    offset: int = 0,
    service: QuestionService = Depends(get_question_service),
    current_user: TokenPaylod = Depends(require_permission("read:questions"))
):
    return {"data": current_user}
    # role = current_user.roles[0] if current_user.roles else None

    # return await service.get_all_question(
    #     limit=limit,
    #     offset=offset,
    #     user_id=current_user.user_id,
    #     is_admin=role
    # )



@router.put("/update/{question_id}")
async def update(
    question_id: int,
    question_data: QuestionUpdate,
    service: QuestionService = Depends(get_question_service),
    current_user: TokenPaylod = Depends(require_permission("update:questions")),
):
    role = current_user.roles[0] if current_user.roles else None

    return await service.update_question(
        question_id=question_id,
        question_data=question_data,
        user_id=current_user.user_id,
        is_admin=role
    )


@router.delete("/delete/{question_id}")
async def delete(
    question_id: int,
    service: QuestionService = Depends(get_question_service),
    current_user: TokenPaylod = Depends(require_permission("delete:questions")),
):
    role = current_user.roles[0] if current_user.roles else None

    return await service.delete_question(
        question_id=question_id,
        user_id=current_user.user_id,
        is_admin=role
    )


