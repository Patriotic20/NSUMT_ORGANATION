from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, Float
from typing import TYPE_CHECKING

from .base import Base
from .mixins.int_id_pk import IntIdPkMixin

if TYPE_CHECKING:
    from .quiz import Quiz
    from .user import User
    from .group import Group
    from .subject import Subject


class Result(Base, IntIdPkMixin):
    __tablename__ = "results"

    # --- Foreign Keys ---
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"))
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)

    # --- Columns ---
    correct_answers: Mapped[int] = mapped_column(Integer, nullable=False)
    incorrect_answers: Mapped[int] = mapped_column(Integer, nullable=False)
    grade: Mapped[float] = mapped_column(Float, nullable=False)

    # --- Relationships ---
    

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="results")
    
    student: Mapped["User"] = relationship(
        "User",
        foreign_keys=[student_id],
        back_populates="student_results"
    )
    teacher: Mapped["User"] = relationship(
        "User",
        foreign_keys=[teacher_id],
        back_populates="teacher_results"
    )
    group: Mapped["Group"] = relationship("Group", back_populates="results")
    
    subject: Mapped["Subject"] = relationship("Subject", back_populates="results")
