from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from .mixins.user_fk_id import UserFkId
from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chair import Chair

class Teacher(Base, IntIdPkMixin, UserFkId):
    
    _user_back_populates = "teacher"

    chair_id: Mapped[int] = mapped_column(ForeignKey("chairs.id" , ondelete="CASCADE"))
    
    first_name: Mapped[str]
    last_name: Mapped[str]
    patronymic: Mapped[str]
    
    chair: Mapped["Chair"] = relationship("Chair" , back_populates="teachers")
    

