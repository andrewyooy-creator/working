from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from app.database import engine, Base
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.database import get_db 
from app.models import Category, Product, Stock, Movement, MovementType
from app import schemas

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Warehouse Management API", version="1.0.0",lifespan=lifespan)

@app.get("/categories", response_model=List[schemas.CategoryResponse], tags=["Categories"])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    return result.scalars().all()

@app.post("/categories", response_model=schemas.CategoryResponse, tags=["Categories"])
async def create_category(category: schemas.CategoryCreate, db: AsyncSession = Depends(get_db)):
    new_cat = Category(**category.model_dump())
    db.add(new_cat)
    await db.commit()
    await db.refresh(new_cat)
    return new_cat

@app.post("/products", response_model=schemas.ProductResponse, tags=["Products"])
async def create_product(product: schemas.ProductCreate, db: AsyncSession = Depends(get_db)):
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

@app.get("/products", response_model=List[schemas.ProductResponse], tags=["Products"])
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

@app.get("/products/{product_id}", response_model=schemas.ProductResponse, tags=["Products"])
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Product).options(selectinload(Product.stock)).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product

@app.post("/movements", response_model=schemas.MovementResponse, tags=["Movements"])
async def create_movement(movement: schemas.MovementCreate, db: AsyncSession = Depends(get_db)):
    if movement.quantity == 0:
        raise HTTPException(status_code=400, detail="Количество должно быть отлично от 0")

    stock_query = select(Stock).where(Stock.product_id == movement.product_id).with_for_update()
    result = await db.execute(stock_query)
    stock = result.scalar_one_or_none()

    if not stock:
        raise HTTPException(status_code=404, detail="Складская запись не найдена")

    abs_quantity = abs(movement.quantity)

    if movement.type == MovementType.OUT:
        if stock.quantity < abs_quantity:
            raise HTTPException(status_code=400, detail=f"Недостаточно товара. Доступно: {stock.quantity}")
        stock.quantity -= abs_quantity
        actual_quantity = -abs_quantity
    else: 
        stock.quantity += abs_quantity
        actual_quantity = abs_quantity

    new_movement = Movement(
        product_id=movement.product_id,
        quantity=actual_quantity,
        type=movement.type
    )
    db.add(new_movement)
    await db.commit()
    await db.refresh(new_movement)
    
    return new_movement

@app.get("/movements/{product_id}", response_model=List[schemas.MovementResponse], tags=["Movements"])
async def get_movements_by_product(product_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Movement).where(Movement.product_id == product_id).order_by(Movement.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()
