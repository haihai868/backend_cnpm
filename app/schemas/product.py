from typing import Optional

from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    description: str
    old_price: Optional[float] = None
    price: float
    size: str
    quantity_in_stock: int
    category_id: int
    image: Optional[str] = None
    age_gender: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    old_price: Optional[float] = None
    price: float
    size: Optional[str] = None
    quantity_in_stock: int
    category_id: int
    image: Optional[str] = None
    age_gender: Optional[str] = None