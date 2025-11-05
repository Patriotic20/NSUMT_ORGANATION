from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from sqlalchemy.orm import relationship

from .base import Base
from .mixins.int_id_pk import IntIdPkMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .subject_teacher_association import SubjectTeacher
    from .questions import Question
    from .quiz import Quiz


class Subject(Base, IntIdPkMixin):
    
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    
    
    subject_teachers: Mapped[list["SubjectTeacher"]] = relationship(
        "SubjectTeacher",
        back_populates="subject",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="subject",
        cascade="all, delete-orphan"
    )
    
    
    quizzes: Mapped[list["Quiz"]] = relationship(
        "Quiz",
        back_populates="subject",
        cascade="all, delete-orphan"
    )
    
    results = relationship(
        "Result",
        back_populates="subject"
    )
