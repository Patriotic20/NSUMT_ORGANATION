from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from .base import Base
from .mixins.int_id_pk import IntIdPkMixin

from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .role import Role

class UserRole(Base, IntIdPkMixin):
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))
    
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_roles"
    )
    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="user_roles"
    )
