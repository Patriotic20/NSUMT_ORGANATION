from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship 

from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from .mixins.user_fk_id import UserFkId

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .department import Department


class Worker(Base, IntIdPkMixin, UserFkId):
    
    _user_back_populates = "worker"

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id" , ondelete="CASCADE"))

    first_name: Mapped[str]
    last_name: Mapped[str]
    patronymic: Mapped[str]

    department: Mapped["Department"] = relationship("Department", back_populates="workers")


