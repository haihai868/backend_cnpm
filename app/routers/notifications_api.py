from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app import schemas, models, security
from app.services import notifications_service
from app.database_connect import get_db

router = APIRouter(
    prefix='/notifications',
    tags=['notifications']
)

@router.get('/', response_model=List[schemas.NotificationOut])
def get_all_notifications(db: Session = Depends(get_db)):
    return notifications_service.get_all_notifications(db)

@router.post('/', status_code=201, response_model=schemas.NotificationOut)
def create_notification(notification: schemas.NotificationCreate, db: Session = Depends(get_db)):
    return notifications_service.create_notification(notification, db)

@router.post('/users', status_code=201)
def create_notification_for_all_user(notification: schemas.NotificationBase, db: Session = Depends(get_db)):
    return notifications_service.create_notification_for_all_user(notification, db)

@router.get("/{id}", response_model=schemas.NotificationOut)
def get_notification(id: int, db: Session = Depends(get_db)):
    return notifications_service.get_notification(id, db)

@router.delete("/{id}")
def delete_notification(id: int, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    return notifications_service.delete_notification(id, db, user)

@router.delete("/admin/{id}")
def delete_user_notifications(id: int, db: Session = Depends(get_db), user: models.Admin = Depends(security.get_current_admin)):
    return notifications_service.delete_user_notifications_admin(id, db)

@router.delete("/")
def delete_user_notifications(db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    return notifications_service.delete_user_notifications(db, user)

@router.get("/user/{user_id}", response_model=List[schemas.NotificationOut])
def get_user_notifications(user_id: int, db: Session = Depends(get_db)):
    return notifications_service.get_user_notifications(user_id, db)

@router.put("/{id}", response_model=schemas.NotificationOut)
def mark_as(id: int, db: Session = Depends(get_db)):
    return notifications_service.mark_as(id, db)
