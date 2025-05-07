from datetime import datetime

from pydantic import BaseModel


class ReportCreate(BaseModel):
    message: str

class ReportOut(BaseModel):
    id: int
    user_id: int
    fullname: str
    message: str
    created_at: datetime