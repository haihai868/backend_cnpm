from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    fullname: str

class UserUpdatePassword(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    password: str
    fullname: str

class TokenData(BaseModel):
    id: Optional[int] = None
    email: Optional[EmailStr] = None

class EmailSchema(BaseModel):
    email: EmailStr