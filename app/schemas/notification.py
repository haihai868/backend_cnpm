from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str

class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: str