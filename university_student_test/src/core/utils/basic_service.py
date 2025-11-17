import logging
from typing import Generic, TypeVar, Type, Any, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, or_, delete
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

from datetime import datetime


from core.models import Base

log = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
DEFAULT_START_TIME = datetime(1970, 1, 1, 0, 0, 0)


class BasicService(Generic[ModelType, SchemaType]):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, model: Type[ModelType], obj_items: SchemaType):
        try:
            log.debug(f"Creating {model.__name__} with data: {obj_items}")
            db_obj = model(**obj_items.model_dump())
            self.db.add(db_obj)
            await self.db.flush()
            await self.db.refresh(db_obj)
            log.info(f"{model.__name__} created with ID: {getattr(db_obj, 'id', None)}")
            return db_obj
        except SQLAlchemyError as e:
            log.exception(f"Failed to create {model.__name__}")
            await self.db.rollback()
            raise e

    async def get(
        self,
        model: Type[ModelType],
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Sequence] = None,
    ):
        try:
            log.debug(
                f"Fetching all {model.__name__} with limit={limit}, offset={offset}, filters={filters}"
            )
            stmt = select(model).offset(offset).limit(limit)
            if filters:
                stmt = stmt.where(and_(*filters))
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            log.exception(f"Failed to fetch all {model.__name__}")
            await self.db.rollback()
            raise e

    async def update(
        self,
        model: Type[ModelType],
        update_data: dict[str, Any] | BaseModel,
        filters: Optional[Sequence] = None,
    ):
        try:
            if isinstance(update_data, BaseModel):
                update_data = update_data.model_dump(exclude_unset=True)

            if not filters:
                raise ValueError("Update requires at least one filter condition.")

            # 🔑 filter out "default-ish" values
            clean_data = {
                k: v for k, v in update_data.items()
                if v not in (None, "", 0, "string", DEFAULT_START_TIME)
            }

            if not clean_data:
                log.warning(f"No valid fields to update for {model.__name__}")
                return None

            log.debug(f"Updating {model.__name__} with {clean_data} and filters {filters}")

            stmt = (
                update(model)
                .where(and_(*filters))
                .values(clean_data)
                .returning(model)  # ✅ return updated rows
                .execution_options(synchronize_session="fetch")
            )

            result = await self.db.execute(stmt)
            await self.db.commit()

            updated_rows = result.fetchall()

            if not updated_rows:
                log.warning(f"No records updated in {model.__name__}")
                return None

            log.info(f"Updated {len(updated_rows)} record(s) in {model.__name__}")

            # ✅ return the updated objects (converted to dicts)
            return [dict(row._mapping) for row in updated_rows]

        except SQLAlchemyError as e:
            log.exception(f"Failed to update {model.__name__}")
            await self.db.rollback()
            raise e



    async def delete(
        self,
        model: Type[ModelType],
        filters: Optional[Sequence] = None,
    ):
        try:
            if not filters:
                raise ValueError("Delete requires at least one filter condition.")

            log.debug(f"Deleting from {model.__name__} with filters {filters}")

            stmt = delete(model).where(and_(*filters))
            result = await self.db.execute(stmt)
            await self.db.commit()

            if result.rowcount == 0:
                log.warning(f"No records deleted in {model.__name__}")
            else:
                log.info(f"Deleted {result.rowcount} record(s) from {model.__name__}")

            return result.rowcount
        except SQLAlchemyError as e:
            log.exception(f"Failed to delete from {model.__name__}")
            await self.db.rollback()
            raise e
