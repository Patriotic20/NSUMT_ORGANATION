from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.subject import Subject
    from core.models.teacher import Teacher


class SubjectTeacher(Base, IntIdPkMixin):
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id", ondelete="CASCADE"))

    subject: Mapped["Subject"] = relationship("Subject", back_populates="subject_teachers")
    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="subject_teachers")
