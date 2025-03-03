from typing import Optional

from pydantic import BaseModel


class OrderCreate(BaseModel):
    user_id: int
    description: Optional[str] = None

    class Config:
        orm_mode = True

class OrderOut(BaseModel):
    id: int
    user_id: int
    created_at: str
    description: Optional[str] = None
    status: str

    class Config:
        orm_mode = True