from fastapi import APIRouter



router = APIRouter(
    tags=["Role Permission"],
    prefix="/role_permission"
)


@router.post("/create")
async def create():
    pass


@router.get("/get/{id}")
async def get_by_id():
    pass


@router.get("/get/all")
async def get_all():
    pass


@router.put("/update/{id}")
async def update(
    id: int
):
    pass


@router.delete("/delete/{id}")
async def delete(
    id: int
):
    pass
