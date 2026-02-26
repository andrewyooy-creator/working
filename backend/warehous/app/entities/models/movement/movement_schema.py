from pydantic import BaseModel,ConfigDict
from warehous.app.entities.models.movement.movement import MovementType
from datetime import datetime

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
