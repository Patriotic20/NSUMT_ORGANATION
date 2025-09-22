from sqlalchemy.orm import Mapped , relationship

from .mixins.int_id_pk import IntIdPkMixin
from .base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .student import Student
    from .teacher import Teacher
    from .worker import Worker
    from .role import Role


class User(Base , IntIdPkMixin):
    
    username: Mapped[str]
    password: Mapped[str]
    
    
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users"
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
        'Worker', 
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        passive_deletes=True  
        )
    
