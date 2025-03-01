from datetime import datetime

from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    size: str
    quantity_in_stock: int
    category_id: int

class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    size: str
    quantity_in_stock: int
    category_id: int