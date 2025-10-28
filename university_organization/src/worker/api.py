from fastapi import APIRouter , Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.utils.database import db_helper
from .schemas import (
    WorkerBase,
    WorkerCreate,
    WorkerResponse,
    WorkerUpdate,
)
from .service import WorkerService , WorkerGet

from core.models.user import User
from core.schemas.get_all import GetAll
from auth.utils.dependencies import require_permission
from auth.schemas.auth import TokenPaylod

router = APIRouter(
    tags=["Workers"],
    prefix="/workers",
)

def get_worker_service(session: AsyncSession = Depends(db_helper.session_getter)):
    return WorkerService(session=session)


@router.post("/create")
async def create(
    create_data: WorkerBase, 
    service: WorkerService = Depends(get_worker_service),
    current_user: TokenPaylod = Depends(require_permission("create:workers"))
    ):
    create_data = WorkerCreate(
        user_id=current_user.user_id,
        **create_data.model_dump()
    )
    return await service.create(create_data=create_data)


@router.get("", response_model=list[WorkerResponse])
async def get_all(
    pagination: GetAll = Depends(), 
    service: WorkerService = Depends(get_worker_service),
    _: User = Depends(require_permission("read:workers"))
):
    return await service.get_all(pagination=pagination)


@router.get("/get/{id}", response_model=WorkerResponse)
async def get_by_id(
    worker_get: WorkerGet = Depends(),
    service: WorkerService = Depends(get_worker_service),
    _: User = Depends(require_permission("read:workers"))
    ):
    return await service.get_by_id(worker_get=worker_get)


@router.put("/update/{id}", response_model=WorkerResponse)
async def update(
    update_data: WorkerUpdate,
    worker_get: WorkerGet = Depends(),
    service: WorkerService = Depends(get_worker_service),
    _: User = Depends(require_permission("update:workers"))
    ):
    return await service.update(worker_get=worker_get, update_data=update_data)
    
@router.delete("/delete/{id}")
async def delete(
    worker_get: WorkerGet = Depends(),
    service: WorkerService = Depends(get_worker_service),
    _: User = Depends(require_permission("delete:workers"))
    
    ):
    await service.delete(worker_get=worker_get)
    return {"message": "Worker deleted successfully"}


