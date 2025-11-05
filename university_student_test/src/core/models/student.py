from sqlalchemy.orm import Mapped, mapped_column , relationship
from datetime import date
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from .mixins.user_fk_id import UserFkId

if TYPE_CHECKING:
    from .group import Group



class Student(Base, IntIdPkMixin, UserFkId):
    
    _user_back_populates = "student"
    
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id" , ondelete="CASCADE"))


    first_name: Mapped[str]
    last_name: Mapped[str]
    third_name: Mapped[str]
    full_name: Mapped[str]
    student_id_number: Mapped[str]
    image_path: Mapped[str]
    birth_date: Mapped[date]
    passport_pin: Mapped[str | None] = mapped_column(nullable=True)
    passport_number: Mapped[str | None] = mapped_column(nullable=True)
    phone: Mapped[str]
    gender: Mapped[str]
    university: Mapped[str]
    specialty: Mapped[str]
    student_status: Mapped[str]  # was studentStatus
    education_form: Mapped[str]  # was educationForm
    education_type: Mapped[str]  # was educationType
    payment_form: Mapped[str]  # was paymentForm
    education_lang: Mapped[str] 
    faculty: Mapped[str | None] = mapped_column(nullable=True)
    level: Mapped[str]
    semester: Mapped[str]
    address: Mapped[str]
    avg_gpa: Mapped[float]
    
    
    group: Mapped["Group"] = relationship("Group", back_populates="students")
