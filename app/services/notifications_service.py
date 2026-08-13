from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.repositories import notifications_repository


def get_all_notifications(db: Session) -> List[models.Notification]:
    return notifications_repository.get_all_notifications(db)


def create_notification(notification: schemas.NotificationCreate, db: Session) -> models.Notification:
    return notifications_repository.create_notification(db, notification.model_dump())


def create_notification_for_all_user(notification: schemas.NotificationBase, db: Session):
    return notifications_repository.create_notification_for_all_users(db, notification.model_dump())


def get_notification(id: int, db: Session) -> models.Notification:
    notification = notifications_repository.get_notification_by_id(db, id)
    if not notification:
        raise HTTPException(status_code=404, detail='Notification not found')
    return notification


def delete_notification(id: int, db: Session, user: models.User):
    notification = notifications_repository.get_notification_by_id(db, id)
    if not notification:
        raise HTTPException(status_code=404, detail='Notification not found')

    if notification.user_id != user.id:
        raise HTTPException(status_code=403, detail='You can only delete your own notifications')

    notifications_repository.delete_notification(db, id)
    return {'message': 'Notification deleted successfully'}


def delete_user_notifications_admin(id: int, db: Session):
    ok = notifications_repository.delete_notification(db, id)
    if not ok:
        raise HTTPException(status_code=404, detail='Notification not found')
    return {'message': 'Notifications deleted successfully'}


def delete_user_notifications(db: Session, user: models.User):
    notifications_repository.delete_user_notifications(db, user.id)
    return {'message': 'Notifications deleted successfully'}


def get_user_notifications(user_id: int, db: Session):
    return notifications_repository.get_user_notifications(db, user_id)


def mark_as(id: int, db: Session):
    notification = notifications_repository.toggle_read(db, id)
    if not notification:
        raise HTTPException(status_code=404, detail='Notification not found')
    return notification
