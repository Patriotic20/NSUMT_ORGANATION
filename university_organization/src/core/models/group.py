from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import ForeignKey

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .faculty import Faculty
    from .student import Student
    from .group_teacher import GroupTeacher
    from .quiz import Quiz
    from .results import Result

class Group(Base, IntIdPkMixin):
    __tablename__ = "groups"
    
    faculty_id: Mapped[int] = mapped_column(ForeignKey("facultys.id" , ondelete="CASCADE"))
    
    name: Mapped[str]
    
    faculty: Mapped["Faculty"] = relationship("Faculty" , back_populates="groups") 
    
    students: Mapped[list["Student"]] = relationship(
        "Student", 
        back_populates="group",
        cascade="all, delete-orphan",  
        passive_deletes=True  
        )
    
    group_teachers: Mapped[list["GroupTeacher"]] = relationship(
        "GroupTeacher",
        back_populates="group",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    
    quizzes: Mapped[list["Quiz"]] = relationship(
        "Quiz",
        back_populates="group",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    results: Mapped[list["Result"]] = relationship(
        "Result",
        back_populates="group",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

   
    
    