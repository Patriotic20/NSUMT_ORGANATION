from .base import Base
from .mixins.int_id_pk import IntIdPkMixin


from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .quiz import Quiz
    from .questions import Question

class UserAnswer(Base, IntIdPkMixin):
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    options: Mapped[str] 
    
    
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_answers"
    )
    
    quiz: Mapped["Quiz"] = relationship(
        "Quiz",
        back_populates="user_answers"
    )
    
    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="user_answers"
    )
    
    
