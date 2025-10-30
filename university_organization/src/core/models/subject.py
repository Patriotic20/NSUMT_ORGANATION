from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from sqlalchemy.orm import relationship

from .base import Base
from .mixins.int_id_pk import IntIdPkMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .teacher import Teacher


class Subject(Base, IntIdPkMixin):
    
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    
    
    teachers: Mapped[list["Teacher"]] = relationship(
        "Teacher",
        secondary = "subject_teachers",
        back_populates = "subjects"
    )
    
    
