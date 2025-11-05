from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Enum, ForeignKey
from datetime import datetime
from typing import TYPE_CHECKING
import enum

from .base import Base
from .mixins.int_id_pk import IntIdPkMixin

if TYPE_CHECKING:
    from .results import Result
    from .question_quiz import QuestionQuiz
    from .user import User
    from .group import Group
    from .subject import Subject


class QuizStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Quiz(Base, IntIdPkMixin):
    __tablename__ = "quizzes"
    
    # --- Foreign Keys ---
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True
    )

    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True
    )

    subject_id: Mapped[int | None] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=True
    )

    # --- Columns ---
    quiz_name: Mapped[str] = mapped_column(String(255), nullable=False)
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    quiz_time: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=False)
    quiz_pin: Mapped[str] = mapped_column(String(100), nullable=False)

    status: Mapped["QuizStatus"] = mapped_column(
        Enum(QuizStatus, native_enum=False),
        nullable=False,
        default=QuizStatus.NOT_STARTED
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(
        "User",
        back_populates="quizzes"
    )

    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="quizzes"
    )

    subject: Mapped["Subject"] = relationship(
        "Subject",
        back_populates="quizzes"
    )

    results: Mapped[list["Result"]] = relationship(
        "Result",
        back_populates="quiz",
        cascade="all, delete-orphan"
    )

    question_quizzes: Mapped[list["QuestionQuiz"]] = relationship(
        "QuestionQuiz",
        back_populates="quiz",
        cascade="all, delete-orphan"
    )

    # --- Helper Property ---
    @property
    def current_status(self) -> QuizStatus:
        """Returns the current status of the quiz dynamically based on time."""
        now = datetime.now().replace(microsecond=0)

        if now < self.start_time:
            return QuizStatus.NOT_STARTED
        if self.start_time <= now <= self.end_time:
            return QuizStatus.IN_PROGRESS
        return QuizStatus.FINISHED
