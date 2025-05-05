from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SaleCreate(BaseModel):
    discount_percentage: float
    age_gender: Optional[str] = None
    category_id: Optional[int] = None

class SaleOut(BaseModel):
    id: int
    discount_percentage: float
    start_date: datetime
    end_date: Optional[datetime] = None
    age_gender: Optional[str] = None
    category_id: Optional[int] = None