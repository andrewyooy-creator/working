from fastapi import APIRouter,HTTPException,Depends
from warehous.app.entities.models.movement.movement import Movement,MovementType
from warehous.app.entities.models.movement.movement_schema import MovementCreate,MovementResponse,MovementType
from warehous.app.entities.models.stock.stock import Stock
from warehous.app.frd.database.database import get_db
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter()

@router.post("/movements", response_model=MovementResponse, tags=["Movements"])
async def create_movement(movement: MovementCreate, db: AsyncSession = Depends(get_db)):
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

@router.get("/movements/{product_id}", response_model=List[MovementResponse], tags=["Movements"])
async def get_movements_by_product(product_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Movement).where(Movement.product_id == product_id).order_by(Movement.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

