from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query, Path

from .service import QuizService
from .schemas import QuizBase, QuizUpdate
from auth.schemas.auth import TokenPaylod
from auth.utils.security import require_permission
from core.database.db_helper import db_helper
from core.utils.save_file import save_file


router = APIRouter(
    tags=["Quiz"],
    prefix="/quiz"
)


def get_quiz_service(session: AsyncSession = Depends(db_helper.session_getter)) -> QuizService:
    """Dependency to provide QuizService instance."""
    return QuizService(session=session)


@router.post("/create")
async def create(
    quiz_data: QuizBase,
    service: QuizService = Depends(get_quiz_service),
    _ : TokenPaylod = Depends(require_permission("create:quiz")),
):
    """Create a new quiz."""
    return await service.create_quiz(quiz_data=quiz_data)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
    """Upload a file and return its URL."""
    url_data = save_file(file=file)
    return {"file_url": url_data}


@router.get("/get/{quiz_id}")
async def get_by_id(
    quiz_id: int,
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("read:quiz")),
):
    """Retrieve a quiz by its ID."""
    return await service.get_quiz_by_id(
        quiz_id=quiz_id,
        user_id=current_user.user_id,
        is_admin=current_user.role,
    )


@router.get("")  # Add response model
async def get_all(
    limit: int = Query(20, ge=1, le=100),  
    offset: int = Query(0, ge=0),
    search: str | None = Query(None, max_length=100),  
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("read:quiz")),
):
    """Retrieve all quizzes with pagination."""
    return await service.get_all_quiz(
        user_id=current_user.user_id,
        is_admin=current_user.role,
        limit=limit,
        offset=offset,
        search=search,  
        group_id=current_user.group_id,
    )


@router.patch("/update/{quiz_id}")
async def update(
    quiz_id: int,
    quiz_data: QuizUpdate,
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("update:quiz")),
):
    """Update an existing quiz."""
    return await service.update_quiz(
        quiz_id=quiz_id,
        user_id=current_user.user_id,
        quiz_data=quiz_data,
        is_admin=current_user.role,
    )


@router.put("/toggle_active")
async def toggle_active(
    quiz_id: int,
    active: bool,
    service: QuizService = Depends(get_quiz_service),
    _ : TokenPaylod = Depends(require_permission("update:quiz"))
):
    return await service.toggle_active(quiz_id = quiz_id, active=active)

@router.delete("/delete/{quiz_id}")
async def delete(
    quiz_id: int,
    service: QuizService = Depends(get_quiz_service),
    current_user: TokenPaylod = Depends(require_permission("delete:quiz")),
) -> dict[str, str]:
    """Delete a quiz by ID."""
    await service.delete_quiz(
        quiz_id=quiz_id,
        user_id=current_user.user_id,
        is_admin=current_user.role,
    )
    return {"message": "Deleted successfully"}
