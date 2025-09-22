from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer, Enum, event
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import enum

from .base import Base
from .mixins.int_pr_ky import IntIdPkMixin

if TYPE_CHECKING:
    from .subjects import Subject
    from .results import Result


class QuizStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Quiz(Base, IntIdPkMixin):

    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False
    )
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    quiz_time: Mapped[int] = mapped_column(Integer, nullable=False)  
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=False)
    quiz_pin: Mapped[str] = mapped_column(String, nullable=False)

    status: Mapped[QuizStatus] = mapped_column(
        Enum(QuizStatus, native_enum=False),
        nullable=False,
        default=QuizStatus.NOT_STARTED,
    )

    # relationships
    subject: Mapped["Subject"] = relationship("Subject", back_populates="quiz")
    results: Mapped[list["Result"]] = relationship(
        "Result",
        back_populates="quiz",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        _update_end_time(self)

    @property
    def current_status(self) -> QuizStatus:
        """Returns the current status of the quiz dynamically based on time."""
        now = datetime.now().replace(microsecond=0)

        if now < self.start_time:
            return QuizStatus.NOT_STARTED

        if self.start_time <= now <= self.end_time:
            return QuizStatus.IN_PROGRESS

        return QuizStatus.FINISHED





def _update_end_time(target: Quiz):
    if target.start_time and target.quiz_time:
        target.end_time = target.start_time + timedelta(minutes=target.quiz_time)



def _update_status(target: Quiz):
    now = datetime.now().replace(microsecond=0)

    if now < target.start_time:
        target.status = QuizStatus.NOT_STARTED
    elif target.start_time <= now <= target.end_time:
        target.status = QuizStatus.IN_PROGRESS
    else:
        target.status = QuizStatus.FINISHED
        

@event.listens_for(Quiz, "before_insert")
def set_end_time_before_insert(mapper, connection, target: Quiz):
    _update_end_time(target)
    _update_status(target)



@event.listens_for(Quiz, "before_update")
def set_end_time_before_update(mapper, connection, target: Quiz):
    _update_end_time(target)
    _update_status(target)

