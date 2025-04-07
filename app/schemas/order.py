from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrderCreate(BaseModel):
    user_id: int
    description: Optional[str] = None

class OrderOut(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    description: Optional[str] = None
    status: str

class OrderDetailCreate(BaseModel):
    product_id: int
    quantity: int

class OrderDetailOut(BaseModel):
    id: int
    product_id: int
    order_id: int
    quantity: int
