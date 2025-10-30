from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
import random

from .base import Base
from .mixins.int_pr_ky import IntIdPkMixin


class Question(Base, IntIdPkMixin):
    __tablename__ = "questions"

    subject_id: Mapped[int] = mapped_column(nullable=False)

    text: Mapped[str] = mapped_column(nullable=False)
    option_a: Mapped[str] = mapped_column(nullable=False)  # always correct
    option_b: Mapped[str] = mapped_column(nullable=False)
    option_c: Mapped[str] = mapped_column(nullable=False)
    option_d: Mapped[str] = mapped_column(nullable=False)

    

    
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
