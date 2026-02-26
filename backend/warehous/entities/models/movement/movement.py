from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime
from sqlalchemy import Integer,ForeignKey,Enum,DateTime
from warehous.entities.models.base.base import Base
import enum

class MovementType(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"

class Movement(Base):
    __tablename__ = "movements"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    type: Mapped[MovementType] = mapped_column(Enum(MovementType))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
