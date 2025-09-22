from sqlalchemy.orm import Mapped, mapped_column, declared_attr, relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.role import Role


class RoleIdFk:
    _role_back_populates: str | None = None

    @declared_attr
    def role_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey("roles.id"))

    @declared_attr
    def role(cls) -> Mapped["Role"]:
        return relationship("Role", back_populates=cls._role_back_populates)
