from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from sqlalchemy.orm import Mapped , relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .worker import Worker


class Department(Base, IntIdPkMixin):
    
    name: Mapped[str]
    
    workers: Mapped[list["Worker"]] = relationship(
        "Worker", 
        back_populates="department",
        cascade="all, delete-orphan",  
        passive_deletes=True  
        )

