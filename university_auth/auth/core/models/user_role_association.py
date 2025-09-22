from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from .base import Base
from .mixins.int_id_pk import IntIdPkMixin


class UserRole(Base, IntIdPkMixin):
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))
    