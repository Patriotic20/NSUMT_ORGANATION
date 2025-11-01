from typing import Generic, TypeVar, Type, Any, Optional, TypeAlias
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, delete, func, desc
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from sqlalchemy.sql.elements import ColumnElement
from fastapi import HTTPException, status

from core.models import Base
from core.schemas.get_all import GetAll

ModelType = TypeVar("ModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)

FilterList: TypeAlias = Optional[list[ColumnElement[bool]]]


class BasicService(Generic[ModelType, SchemaType]):
    def __init__(self, session: AsyncSession):
        self.session = session

    
    @staticmethod
    def make_filter(filters: FilterList) -> list[ColumnElement[bool]]:
        if not filters:
            return []
        return [f for f in filters if f is not None]

    async def create(
        self,
        model: Type[ModelType],
        create_data: SchemaType,
        filters: FilterList = None,
    ):
        try:
            if hasattr(create_data, "model_dump"):
                create_data = create_data.model_dump()

            filters = self.make_filter(filters)
            if filters:
                stmt_check = select(model).where(and_(*filters))
                result_check = await self.session.execute(stmt_check)
                existing = result_check.scalar_one_or_none()
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{model.__name__} already exists"
                    )

            db_obj = model(**create_data)
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(db_obj)
            return db_obj

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def get(
            self,
            model: Type["ModelType"],
            filters: Optional["FilterList"] = None,
            pagination: Optional["GetAll"] = None,
            single: bool = False,
        ):
            try:
                filters = self.make_filter(filters)


                stmt = select(model)
                if filters:
                    stmt = stmt.where(and_(*filters))


                if hasattr(model, "id"):
                    stmt = stmt.order_by(desc(model.id))

                # --- Handle single fetch ---
                if single:
                    result = await self.session.execute(stmt)
                    obj = result.scalars().first()
                    if not obj:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{model.__name__} not found"
                        )
                    return obj

                # --- Count total ---
                count_stmt = select(func.count()).select_from(model)
                if filters:
                    count_stmt = count_stmt.where(and_(*filters))
                total = (await self.session.execute(count_stmt)).scalar_one()

                # --- Apply pagination ---
                if pagination:
                    stmt = stmt.offset(pagination.offset).limit(pagination.limit)

                # --- Get data ---
                result = await self.session.execute(stmt)
                data = result.scalars().all()

                if not data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"{model.__name__}(s) not found"
                    )

                return {
                    "total": total,
                    "data": data,
                }

            except SQLAlchemyError as e:
                await self.session.rollback()
                raise e

    async def update(
        self,
        model: Type[ModelType],
        update_data: dict[str, Any] | BaseModel,
        filters: FilterList = None,
        unique_filters: FilterList = None,
    ):
        try:
            if isinstance(update_data, BaseModel):
                update_data = update_data.model_dump(exclude_unset=True)

            filters = self.make_filter(filters)
            if not filters:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Update requires at least one filter condition."
                )

            stmt_check = select(model).where(and_(*filters))
            result_check = await self.session.execute(stmt_check)
            obj = result_check.scalar_one_or_none()
            if not obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{model.__name__} not found"
                )

            unique_filters = self.make_filter(unique_filters)
            if unique_filters:
                stmt_unique = select(model).where(and_(*unique_filters))
                result_unique = await self.session.execute(stmt_unique)
                conflict = result_unique.scalar_one_or_none()
                if conflict and conflict.id != obj.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{model.__name__} with these values already exists"
                    )

            clean_data = {
                k: v for k, v in update_data.items()
                if v not in (None, "", 0, "string")
            }

            if not clean_data:
                return None

            stmt = (
                update(model)
                .where(and_(*filters))
                .values(clean_data)
                .returning(model)
                .execution_options(synchronize_session="fetch")
            )

            result = await self.session.execute(stmt)
            await self.session.commit()
            updated_rows = result.fetchall()
            return [dict(row._mapping) for row in updated_rows]

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def delete(
        self,
        model: Type[ModelType],
        filters: FilterList = None,
    ):
        try:
            filters = self.make_filter(filters)
            if not filters:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Delete requires at least one filter condition."
                )

            stmt_check = select(model).where(and_(*filters))
            result_check = await self.session.execute(stmt_check)
            obj = result_check.scalar_one_or_none()
            if not obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{model.__name__} not found"
                )

            stmt = delete(model).where(and_(*filters))
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
