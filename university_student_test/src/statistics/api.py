from fastapi import APIRouter


router = APIRouter(
    tags=['Statistics'],
    prefix='/statistics'
)

@router.get('/faculty/{id}')
async def faculty_statistics():
    pass

@router.get('/chair/{id}')
async def chair_statistics():
    pass

@router.get('/teacher/{id}')
async def teacher_statistics():
    pass