from .base import Base
from .mixins.int_pr_ky import IntIdPkMixin
from sqlalchemy.orm import Mapped , mapped_column
from sqlalchemy.orm import relationship


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .questions import Question
    from .quiz import Quiz


class Subject(Base , IntIdPkMixin):
    
    teacher_id: Mapped[int| None] =  mapped_column(nullable=True)
    name: Mapped[str]
    
    
    questions: Mapped[list["Question"]] = relationship(
        "Question", 
        back_populates="subject",
        cascade="all, delete-orphan",  
        passive_deletes=True  
        )
    
    quiz: Mapped["Quiz"] = relationship(
        "Quiz",
        back_populates="subject",
        cascade="all, delete-orphan",  
        passive_deletes=True  
        
    )
    

    
    
