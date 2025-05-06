from typing import Optional

from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    description: str
    old_price: Optional[float] = None
    price: float
    size: str
    quantity_in_stock: int
    category_id: int
    image: Optional[str] = None
    age_gender: Optional[str] = None

    model_config = {
        'from_attributes': True
    }

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int

class ProductOrderOut(ProductBase):
    id: int
    quantity_in_order: int

class ProductWithPaidQuantity(BaseModel):
    name: str
    paid_quantity: int
    price: float
    image: Optional[str]

