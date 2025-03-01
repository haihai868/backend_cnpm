from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.database_connect import get_db

router = APIRouter(
    prefix='/notifications',
    tags=['notifications']
)

@router.get('/', response_model=List[schemas.NotificationOut])
def get_all_notifications(db: Session = Depends(get_db)):
    notifications = db.query(models.Notification).all()
    return notifications

@router.post('/', response_model=schemas.NotificationOut)
def create_notification(notification: schemas.NotificationCreate, db: Session = Depends(get_db)):
    new_notification = models.Notification(**notification.model_dump())
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification

@router.get("/{id}", response_model=schemas.NotificationOut)
def get_notification(id: int, db: Session = Depends(get_db)):
    notification = db.query(models.Notification).filter(models.Notification.id == id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification

@router.delete("/{id}")
def delete_notification(id: int, db: Session = Depends(get_db)):
    notification = db.query(models.Notification).filter(models.Notification.id == id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notification)
    db.commit()
    return {'message': 'Notification deleted successfully'}

@router.get("/user/{user_id}", response_model=List[schemas.NotificationOut])
def get_user_notifications(user_id: int, db: Session = Depends(get_db)):
    notifications = db.query(models.Notification).filter(models.Notification.user_id == user_id).all()
    return notifications

@router.delete("/user/{user_id}")
def delete_user_notifications(user_id: int, db: Session = Depends(get_db)):
    notifications = db.query(models.Notification).filter(models.Notification.user_id == user_id).all()
    for notification in notifications:
        db.delete(notification)
    db.commit()
    return {'message': 'Notifications deleted successfully'}

@router.put("/{id}", response_model=schemas.NotificationOut)
def mark_as(id: int, db: Session = Depends(get_db)):
    notification = db.query(models.Notification).filter(models.Notification.id == id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = not notification.is_read
    db.commit()
    db.refresh(notification)
    return notification
