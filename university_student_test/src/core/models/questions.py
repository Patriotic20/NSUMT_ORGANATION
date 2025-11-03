from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
import random
from sqlalchemy.orm import relationship

from .base import Base
from .mixins.int_pr_ky import IntIdPkMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .question_quiz import QuestionQuiz


class Question(Base, IntIdPkMixin):
    __tablename__ = "questions"
    
    
    subject_id: Mapped[int | None] = mapped_column(nullable=True)
    user_id: Mapped[int | None] = mapped_column(nullable=True)

    text: Mapped[str] = mapped_column(nullable=False)
    option_a: Mapped[str] = mapped_column(nullable=False)  
    option_b: Mapped[str] = mapped_column(nullable=False)
    option_c: Mapped[str] = mapped_column(nullable=False)
    option_d: Mapped[str] = mapped_column(nullable=False)
    
    
    question_quizzes: Mapped[list["QuestionQuiz"]] = relationship("QuestionQuiz", back_populates="question")

    

    
    def to_dict(self, randomize_options: bool = True):
        """
        Convert question to dict.
        Randomly shuffles options, but does not show which is correct.
        """
        options = [self.option_a, self.option_b, self.option_c, self.option_d]
        if randomize_options:
            random.shuffle(options)

        return {
            "id": self.id,
            "text": self.text,
            "options": options,
        }
