from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import String,Numeric,ForeignKey
from warehous.entities.models.base.base import Base
from warehous.entities.models.category.category import Category
from warehous.entities.models.stock.stock import Stock
import secrets
import string

def generate_sku() -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(8))


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    sku: Mapped[str] = mapped_column(String, unique=True, index=True, default=generate_sku)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    description: Mapped[str | None] = mapped_column(String)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="products")
    stock: Mapped["Stock"] = relationship(back_populates="product", uselist=False)
