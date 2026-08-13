from typing import List, Optional
from sqlalchemy.orm import Session

from app import models


def create_report(db: Session, data: dict) -> models.Report:
    report = models.Report(**data)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_report_by_id(db: Session, id: int) -> Optional[models.Report]:
    return db.query(models.Report).filter(models.Report.id == id).first()


def delete_report(db: Session, id: int) -> bool:
    report = get_report_by_id(db, id)
    if not report:
        return False
    db.delete(report)
    db.commit()
    return True


def update_report(db: Session, id: int, data: dict) -> Optional[models.Report]:
    report = get_report_by_id(db, id)
    if not report:
        return None
    report.message = data.get('message', report.message)
    db.commit()
    db.refresh(report)
    return report


def get_reports_by_user_id(db: Session, id: int):
    return db.query(models.Report).filter(models.Report.user_id == id).all()


def get_all_reports(db: Session):
    return db.query(models.Report).all()
