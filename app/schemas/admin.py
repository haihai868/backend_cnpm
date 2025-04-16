from pydantic import BaseModel


class AdminCreate(BaseModel):
    password: str
    email: str

class AdminOut(BaseModel):
    id: int
    password: str
    email: str