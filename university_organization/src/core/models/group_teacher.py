from .base import Base
from .mixins.int_id_pk import IntIdPkMixin

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.group import Group
    from core.models.teacher import Teacher

class GroupTeacher(Base, IntIdPkMixin):
    
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id", ondelete="CASCADE"))
    
    
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="teachers",
    )
    teacher: Mapped["Teacher"] = relationship(
        "Teacher",
        back_populates="groups",
    )
