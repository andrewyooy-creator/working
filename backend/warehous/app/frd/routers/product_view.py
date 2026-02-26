from fastapi import APIRouter,Depends,HTTPException
from typing import List,Optional
from warehous.app.entities.models.product.product_schema import ProductResponse,ProductCreate
from warehous.app.entities.models.product.product import Product
from warehous.app.entities.models.stock.stock import Stock
from warehous.app.entities.models.category.category import Category
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from warehous.app.frd.database.database import get_db
from sqlalchemy.orm import selectinload

router = APIRouter()

@router.post("/products", response_model=ProductResponse, tags=["Products"])
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    cat_query = await db.execute(select(Category).where(Category.id == product.category_id))
    if not cat_query.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Категория не найдена")

    new_product = Product(**product.model_dump())
    db.add(new_product)
    await db.flush() 

    new_stock = Stock(product_id=new_product.id, quantity=0)
    db.add(new_stock)
    
    await db.commit()
    
    query = select(Product).options(selectinload(Product.stock)).where(Product.id == new_product.id)
    result = await db.execute(query)
    return result.scalar_one()

@router.get("/products", response_model=List[ProductResponse], tags=["Products"])
async def get_products(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Product).options(selectinload(Product.stock))
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
        
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Product).options(selectinload(Product.stock)).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product