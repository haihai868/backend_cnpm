from datetime import datetime
from enum import Enum

from pydantic import BaseModel

class rating_enum(str, Enum):
    one = '1'
    two = '2'
    three = '3'
    four = '4'
    five = '5'

class ReviewCreate(BaseModel):
    rating: rating_enum
    comment: str
    product_id: int

class ReviewOut(BaseModel):
    id: int
    user_id: int
    rating: rating_enum
    comment: str
    product_id: int
    created_at: datetime