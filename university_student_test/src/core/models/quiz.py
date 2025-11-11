from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from datetime import datetime
from typing import TYPE_CHECKING


from .base import Base
from .mixins.int_id_pk import IntIdPkMixin

if TYPE_CHECKING:
    from .results import Result
    from .question_quiz import QuestionQuiz
    from .user import User
    from .group import Group
    from .subject import Subject
    from .user_answer import UserAnswer



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
    quiz_pin: Mapped[str] = mapped_column(String(100), nullable=False)
    is_activate: Mapped[bool] = mapped_column(nullable=False, default=False)


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
    
    
    user_answers: Mapped[list["UserAnswer"]] = relationship(
        "UserAnswer",
        back_populates="quiz"
    )
    

    
