from sqlalchemy.orm import Mapped, relationship, mapped_column
from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .permission import Permission
    from .role_permission_association import RolePermission
    from .user_role_association import UserRole


class Role(Base, IntIdPkMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
        overlaps="roles",
    )

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        overlaps="user_roles,role",
    )

    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        overlaps="permissions,roles",
    )

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        overlaps="role_permissions,role_permissions.permission,role_permissions.role",
    )
