from sqlalchemy.orm import Mapped , relationship , mapped_column
from .base import Base
from .mixins.int_id_pk import IntIdPkMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .role_permission_association import RolePermission
    from .user_role_association import UserRole



class Role(Base , IntIdPkMixin):
    
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    
    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan"
    )
    
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan"
    )
    

    

