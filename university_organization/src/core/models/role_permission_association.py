from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .role import Role
    from .permission import Permission


class RolePermission(Base, IntIdPkMixin):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"))

    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="role_permissions",
        overlaps="permissions,roles,role_permissions",
    )

    permission: Mapped["Permission"] = relationship(
        "Permission",
        back_populates="role_permissions",
        overlaps="roles,role_permissions,permissions",
    )
