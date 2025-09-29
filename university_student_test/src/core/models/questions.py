from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import ForeignKey 
from typing import TYPE_CHECKING
import random

from .base import Base
from .mixins.int_pr_ky import IntIdPkMixin

if TYPE_CHECKING:
    from .subjects import Subject

class Question(Base, IntIdPkMixin):
    
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id" , ondelete="CASCADE"))
    
    text: Mapped[str | None] = mapped_column(nullable=True)
    image: Mapped[str | None] = mapped_column(nullable=True)
    
    option_a: Mapped[str | None] = mapped_column(nullable=True)
    option_a_image: Mapped[str | None] = mapped_column(nullable=True)
    
    option_b: Mapped[str | None] = mapped_column(nullable=True)
    option_b_image: Mapped[str | None] = mapped_column(nullable=True)
    
    option_c: Mapped[str | None] = mapped_column(nullable=True)
    option_c_image: Mapped[str | None] = mapped_column(nullable=True)
    
    option_d: Mapped[str | None] = mapped_column(nullable=True)
    option_d_image: Mapped[str | None] = mapped_column(nullable=True)
    
    

    subject: Mapped["Subject"] = relationship("Subject" , back_populates="questions")
    
    
    def to_dict(self, randomize_options: bool = True):
        options = []

        if self.option_a or self.option_a_image:
            options.append({"text": self.option_a, "image": self.option_a_image})
        if self.option_b or self.option_b_image:
            options.append({"text": self.option_b, "image": self.option_b_image})
        if self.option_c or self.option_c_image:
            options.append({"text": self.option_c, "image": self.option_c_image})
        if self.option_d or self.option_d_image:
            options.append({"text": self.option_d, "image": self.option_d_image})

        if randomize_options:
            random.shuffle(options)

        return {
            "id": self.id,
            "text": self.text,
            "image": self.image,
            "options": options
        }
