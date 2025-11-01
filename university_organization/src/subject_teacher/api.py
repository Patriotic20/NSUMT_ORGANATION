from fastapi import APIRouter

from .schemas import SubjectTeacherCreate


router = APIRouter(
    tags=["Subject Teacher"],
    prefix="/subject_teacher"
)


@router.post("/create")
async def create(
    create_data: SubjectTeacherCreate
):
    pass

@router.get("/get/{id}")
async def get_by_id(
    id: int
):
    pass

