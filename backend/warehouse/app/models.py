import secrets
import string
import enum
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def generate_sku() -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(8))

class MovementType(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(String)
    
    products: Mapped[list["Product"]] = relationship(back_populates="category")

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

class Stock(Base):
    __tablename__ = "stocks"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), unique=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["Product"] = relationship(back_populates="stock")

class Movement(Base):
    __tablename__ = "movements"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    type: Mapped[MovementType] = mapped_column(Enum(MovementType))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
