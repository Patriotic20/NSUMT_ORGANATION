from fastapi import APIRouter , Depends, UploadFile , File
from sqlalchemy.ext.asyncio import AsyncSession

from .service import QuizService 
from .schemas import QuizBase , QuizUpdate , QuizResponse

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



@router.post("/create" , response_model=QuizResponse)
async def create(
    quiz_data: QuizBase,
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("create:quiz"))
):
    return await service.create_quiz(quiz_data=quiz_data, teacher_id=current_user.user_id,)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    url_data = save_file(file=file)
    return {"file_url": url_data}
        
    
    

@router.get("/get/{quiz_id}" , response_model=QuizResponse)
async def get_by_id(
    quiz_id: int,
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("read:quiz"))
):
    return await service.get_quiz_by_id(quiz_id=quiz_id, teacher_id=current_user.user_id)

@router.get("")
async def get_all(
    limit: int = 20,
    offset: int = 0,
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("read:quiz"))
):
    return await service.get_all_quiz(limit=limit, offset=offset , teacher_id=current_user.user_id)

@router.patch("/update/{quiz_id}")
async def update(
    quiz_id: int,
    quiz_data: QuizUpdate,
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("update:quiz"))
):
    return await service.update_quiz(quiz_id=quiz_id, teacher_id=current_user.user_id,  quiz_data=quiz_data)


@router.delete("/delete/{quiz_id}")
async def delete(
    quiz_id: int,
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("delete:quiz"))
):
    await service.delete_quiz(quiz_id=quiz_id, teacher_id=current_user.user_id)
    return {
        "Message" : "Delete successfully"
    }
