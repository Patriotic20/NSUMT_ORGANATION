from .base import Base
from .mixins.int_id_pk import IntIdPkMixin

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey


class RolePermission(Base, IntIdPkMixin):
    
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"))
    
    
    
