from fastapi import APIRouter



router = APIRouter(
    tags=["Result"],
    prefix="/result"
)



@router.post()
async def create():
    pass

@router.get()
async def get_by_id():
    pass


@router.get()
async def get_all():
    pass

@router.put()
async def update():
    pass

@router.delete()
async def delete():
    pass

