from fastapi import APIRouter, Depends
from core.schemas.get_all import GetAll

router = APIRouter(
    tags=["Group Teacher"],
    prefix="/group_teahcer"
)


@router.post()
async def create(
    create_data
):
    pass


@router.get("/get/{id}")
async def get_by_id(
    id: int,
    group_id: int | None = None,
    teacher_id: int | None = None,
):
    pass

@router.get()
async def get_all(
    pagination: GetAll = Depends()
):
    pass

@router.put("/update")
async def update(
    update_data 
):
    pass

@router.delete("/delete/{id}")
async def delete(
    id: int,
    group_id: int | None = None,
    teacher_id: int | None = None,
):
    pass

