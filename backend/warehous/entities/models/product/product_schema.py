from pydantic import BaseModel,Field,ConfigDict
from typing import Optional
from warehous.entities.models.stock.stock_schema import StockResponse

class ProductBase(BaseModel):
    name: str
    price: float = Field(gt=0)
    description: Optional[str] = None
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    sku: str
    stock: Optional[StockResponse] = None
    model_config = ConfigDict(from_attributes=True)