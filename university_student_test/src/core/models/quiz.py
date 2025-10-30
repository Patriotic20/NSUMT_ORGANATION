from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer, Enum, Table, Column
from datetime import datetime
from typing import TYPE_CHECKING
import enum

from .base import Base
from .mixins.int_pr_ky import IntIdPkMixin

if TYPE_CHECKING:
    from .results import Result
    from .questions import Question


quiz_questions = Table(
    "quiz_questions",
    Base.metadata,
    Column("quiz_id", ForeignKey("quizzes.id", ondelete="CASCADE"), primary_key=True),
    Column("question_id", ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True),
)


class QuizStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Quiz(Base, IntIdPkMixin):
    __tablename__ = "quizzes"

    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    quiz_time: Mapped[int] = mapped_column(Integer, nullable=False)  # in seconds or minutes
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=False)
    quiz_pin: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    status: Mapped[QuizStatus] = mapped_column(
        Enum(QuizStatus, native_enum=False),
        nullable=False,
        default=QuizStatus.NOT_STARTED,
    )

    # Many-to-many: one quiz can have multiple questions
    question_quizzes: Mapped[list["QuestionQuiz"]] = relationship(
        "QuestionQuiz",
        back_populates="quiz",
        cascade="all, delete-orphan",
    )

    questions: Mapped[list["Question"]] = relationship(
        "Question",
        secondary="question_quizzes",
        back_populates="quizzes",
        viewonly=True,
    )

    @property
    def current_status(self) -> QuizStatus:
        """Returns the current status of the quiz dynamically based on time."""
        now = datetime.now().replace(microsecond=0)

        if now < self.start_time:
            return QuizStatus.NOT_STARTED

        if self.start_time <= now <= self.end_time:
            return QuizStatus.IN_PROGRESS

        return QuizStatus.FINISHED






        


