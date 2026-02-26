from fastapi import APIRouter,Depends
from warehous.app.entities.models.category.category import Category
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from warehous.app.entities.models.category.category_schema import CategoryCreate,CategoryResponse
from typing import List
from warehous.app.frd.database.database import get_db
router = APIRouter()

@router.get("/categories", response_model=List[CategoryResponse], tags=["Categories"])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    return result.scalars().all()

@router.post("/categories", response_model=CategoryResponse, tags=["Categories"])
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_db)):
    new_cat = Category(**category.model_dump())
    db.add(new_cat)
    await db.commit()
    await db.refresh(new_cat)
    return new_cat