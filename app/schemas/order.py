from pydantic import BaseModel


class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

    class Config:
        orm_mode = True

class OrderOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    created_at: str
    updated_at: str
    status: str

    class Config:
        orm_mode = True