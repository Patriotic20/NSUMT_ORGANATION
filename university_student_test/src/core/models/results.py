from .base import Base
from .mixins.int_pr_ky import IntIdPkMixin
from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import ForeignKey , DateTime , Integer , Float
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .quiz import Quiz

class Result(Base , IntIdPkMixin):
    
    
    student_id: Mapped[int]
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizs.id" , ondelete="CASCADE"), nullable=False)

    correct_answers: Mapped[int] = mapped_column(Integer, nullable=False)
    incorrect_answers: Mapped[int] = mapped_column(Integer, nullable=False)
    grade: Mapped[float] = mapped_column(Float, nullable=False)
    
    quiz: Mapped["Quiz"] = relationship("Quiz" , back_populates="results")
