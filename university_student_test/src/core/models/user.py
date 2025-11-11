from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from .mixins.int_id_pk import IntIdPkMixin
from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .student import Student
    from .teacher import Teacher
    from .worker import Worker
    from .role import Role
    from .user_role_association import UserRole
    from .questions import Question
    from .quiz import Quiz
    from .results import Result
    from .user_answer import UserAnswer


class User(Base, IntIdPkMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)


    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates = "users",
        overlaps="user_roles"
    )

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        passive_deletes=True
    )

    teacher: Mapped["Teacher"] = relationship(
        "Teacher",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        passive_deletes=True
    )

    worker: Mapped["Worker"] = relationship(
        "Worker",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        passive_deletes=True
    )

    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    quizzes: Mapped[list["Quiz"]] = relationship(
        "Quiz",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Optional: link Results if using users for student/teacher
    student_results: Mapped[list["Result"]] = relationship(
        "Result",
        back_populates="student",
        foreign_keys="[Result.student_id]",
        cascade="all, delete-orphan"
    )

    teacher_results: Mapped[list["Result"]] = relationship(
        "Result",
        back_populates="teacher",
        foreign_keys="[Result.teacher_id]",
        cascade="all, delete-orphan"
    )
    
    user_answers: Mapped[list["UserAnswer"]] = relationship(
        "UserAnswer",
        back_populates="user"
    )
