from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, Float
from typing import TYPE_CHECKING

from .base import Base
from .mixins.int_pr_ky import IntIdPkMixin

if TYPE_CHECKING:
    from .quiz import Quiz


class Result(Base, IntIdPkMixin):
    __tablename__ = "results"

    student_id: Mapped[int] = mapped_column(nullable=False)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)

    correct_answers: Mapped[int] = mapped_column(Integer, nullable=False)
    incorrect_answers: Mapped[int] = mapped_column(Integer, nullable=False)
    grade: Mapped[float] = mapped_column(Float, nullable=False)

    # Each result belongs to one quiz
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="results")
