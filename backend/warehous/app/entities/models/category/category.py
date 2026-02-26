from warehous.app.entities.models.base.base import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import String
from warehous.app.entities.models.product.product import Product

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(String)
    products: Mapped[list["Product"]] = relationship(back_populates="category")


