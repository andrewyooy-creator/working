from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from app.models import MovementType

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class StockResponse(BaseModel):
    quantity: int
    model_config = ConfigDict(from_attributes=True)

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

class MovementCreate(BaseModel):
    product_id: int
    quantity: int
    type: MovementType

class MovementResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    type: MovementType
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
