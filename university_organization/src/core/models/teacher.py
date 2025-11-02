from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from .mixins.user_fk_id import UserFkId
from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chair import Chair
    from .group_teacher import GroupTeacher
    from .subject_teacher_association import SubjectTeacher

class Teacher(Base, IntIdPkMixin, UserFkId):
    
    _user_back_populates = "teacher"

    chair_id: Mapped[int] = mapped_column(ForeignKey("chairs.id" , ondelete="CASCADE"))
    
    first_name: Mapped[str]
    last_name: Mapped[str]
    patronymic: Mapped[str]
    
    chair: Mapped["Chair"] = relationship("Chair" , back_populates="teachers")
    
    
    subject_teachers: Mapped[list["SubjectTeacher"]] = relationship(
        "SubjectTeacher",
        back_populates="teacher",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    group_teachers: Mapped[list["GroupTeacher"]] = relationship(
        "GroupTeacher",
        back_populates="teacher",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

