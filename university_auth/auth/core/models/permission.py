from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING



if TYPE_CHECKING:
    from .role import Role


class Permission(Base, IntIdPkMixin):
    
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
    )
