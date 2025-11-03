from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from core.models.base import Base
from core.models.mixins.int_pr_ky import IntIdPkMixin


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .questions import Question
    from .quiz import Quiz

class QuestionQuiz(Base, IntIdPkMixin):
    __tablename__ = "question_quiz"

    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)

    
    question: Mapped["Question"] = relationship("Question", back_populates="question_quizzes")
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="question_quizzes")
