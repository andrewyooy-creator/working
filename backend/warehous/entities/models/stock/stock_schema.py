from pydantic import BaseModel,ConfigDict

class StockResponse(BaseModel):
    quantity: int
    model_config = ConfigDict(from_attributes=True)
