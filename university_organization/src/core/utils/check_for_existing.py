from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , and_
from fastapi import HTTPException , status


from .service import ModelType , FilterList




async def check_for_existing(
    session: AsyncSession,
    model: type[ModelType],
    filters: FilterList = None,
):
    stmt = select(model).where(and_(*filters))
    result = await session.execute(stmt)
    some_data = result.scalars().first()
    
    if some_data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{model.__name__} in already used"
        )
