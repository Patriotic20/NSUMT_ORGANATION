from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from sqlalchemy.orm import Mapped, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chair import Chair
    from .group import Group


class Faculty(Base, IntIdPkMixin):

    name: Mapped[str]
    
    chairs: Mapped[list["Chair"]] = relationship(
        "Chair", 
        back_populates="faculty",
        cascade="all, delete-orphan",  
        passive_deletes=True
        )
    
    groups: Mapped[list["Group"]] = relationship(
        "Group",
        back_populates="faculty",
        cascade="all, delete-orphan",  
        passive_deletes=True
    )



