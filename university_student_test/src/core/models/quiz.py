from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import String, Integer, Enum
from datetime import datetime
from typing import TYPE_CHECKING
import enum

if TYPE_CHECKING:
    from .results import Result

from .base import Base
from .mixins.int_pr_ky import IntIdPkMixin



class QuizStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Quiz(Base, IntIdPkMixin):
    __tablename__ = "quizzes"
    
    quiz_name: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    group_id: Mapped[int] = mapped_column(Integer, nullable=False)
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    quiz_time: Mapped[int] = mapped_column(Integer, nullable=False)  
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=False)
    quiz_pin: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    status: Mapped[QuizStatus] = mapped_column(
        Enum(QuizStatus, native_enum=False),
        nullable=False,
        default=QuizStatus.NOT_STARTED,
    )
    
    results: Mapped["Result"] = relationship("Result", back_populates="quiz")

    @property
    def current_status(self) -> QuizStatus:
        """Returns the current status of the quiz dynamically based on time."""
        now = datetime.now().replace(microsecond=0)

        if now < self.start_time:
            return QuizStatus.NOT_STARTED

        if self.start_time <= now <= self.end_time:
            return QuizStatus.IN_PROGRESS

        return QuizStatus.FINISHED






        


