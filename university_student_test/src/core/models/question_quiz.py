from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from .base import Base
from .mixins.int_pr_ky import IntIdPkMixin


class QuestionQuiz(Base, IntIdPkMixin):
    __tablename__ = "question_quizzes"

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )

    # Optional relationships (for easy navigation)
    question: Mapped["Question"] = relationship("Question", back_populates="question_quizzes")
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="question_quizzes")
