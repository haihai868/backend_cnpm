from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description: str


class CategoryOut(BaseModel):
    id: int
    name: str
    description: str