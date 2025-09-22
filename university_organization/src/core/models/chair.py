from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from sqlalchemy.orm import Mapped, mapped_column ,relationship 
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .faculty import Faculty
    from .teacher import Teacher


class Chair(Base, IntIdPkMixin):

    faculty_id: Mapped[int] = mapped_column(ForeignKey("facultys.id" , ondelete="CASCADE"))

    name: Mapped[str]
    
    faculty: Mapped["Faculty"] = relationship("Faculty" , back_populates="chairs")  
     
    teachers: Mapped[list["Teacher"]] = relationship(
        "Teacher", 
        back_populates="chair",
        cascade="all, delete-orphan",  
        passive_deletes=True  
        )
