from typing import List, Optional
from sqlalchemy.orm import Session

from app import models


def get_all_notifications(db: Session) -> List[models.Notification]:
    return db.query(models.Notification).all()


def create_notification(db: Session, data: dict) -> models.Notification:
    new_notification = models.Notification(**data)
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification


def create_notification_for_all_users(db: Session, data: dict):
    users = db.query(models.User).all()
    for user in users:
        new_notification = models.Notification(**data, user_id=user.id)
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)


def get_notification_by_id(db: Session, id: int) -> Optional[models.Notification]:
    return db.query(models.Notification).filter(models.Notification.id == id).first()


def delete_notification(db: Session, id: int) -> bool:
    notification = db.query(models.Notification).filter(models.Notification.id == id).first()
    if not notification:
        return False
    db.delete(notification)
    db.commit()
    return True


def get_user_notifications(db: Session, user_id: int):
    return db.query(models.Notification).filter(models.Notification.user_id == user_id).all()


def get_notifications_by_user(db: Session, user_id: int):
    return db.query(models.Notification).filter(models.Notification.user_id == user_id).all()


def delete_user_notifications(db: Session, user_id: int):
    notifications = db.query(models.Notification).filter(models.Notification.user_id == user_id).all()
    for notification in notifications:
        db.delete(notification)
    db.commit()


def toggle_read(db: Session, id: int):
    notification = db.query(models.Notification).filter(models.Notification.id == id).first()
    if not notification:
        return None
    notification.is_read = not notification.is_read
    db.commit()
    db.refresh(notification)
    return notification
