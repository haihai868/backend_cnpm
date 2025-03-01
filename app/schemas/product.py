from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    description: str
    old_price: Optional[float]
    price: float
    size: str
    quantity_in_stock: int
    category_id: int
    image: Optional[str]

class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    old_price: Optional[float]
    price: float
    size: str
    quantity_in_stock: int
    category_id: int
    image: Optional[str]