from typing import Optional
from sqlalchemy.orm import Session

from app import models


def get_admin_by_id(db: Session, id: int) -> Optional[models.Admin]:
    return db.query(models.Admin).filter(models.Admin.id == id).first()


def get_admin_by_email(db: Session, email: str) -> Optional[models.Admin]:
    return db.query(models.Admin).filter(models.Admin.email == email).first()


def create_admin(db: Session, data: dict) -> models.Admin:
    admin = models.Admin(**data)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def update_admin(db: Session, admin_id: int, data: dict):
    q = db.query(models.Admin).filter(models.Admin.id == admin_id)
    q.update(data, synchronize_session=False)
    db.commit()
    return q.first()
