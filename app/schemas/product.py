from typing import Optional

from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str
    description: str
    old_price: Optional[float] = None
    price: float
    size: str
    quantity_in_stock: int
    category_id: int
    image: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    old_price: Optional[float] = None
    price: float
    size: str
    quantity_in_stock: int
    category_id: int
    image: Optional[str] = None