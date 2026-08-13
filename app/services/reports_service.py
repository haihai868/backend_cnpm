from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.repositories import reports_repository


def create_report(report: schemas.ReportCreate, db: Session, user: models.User):
    report_obj = report.model_dump()
    report_obj.update({'user_id': user.id})
    r = reports_repository.create_report(db, report_obj)
    r.fullname = user.fullname
    return r


def delete_report(id: int, db: Session, user: models.User):
    report = reports_repository.get_report_by_id(db, id)
    if not report:
        raise HTTPException(status_code=404, detail='Report not found')

    if report.user_id != user.id:
        raise HTTPException(status_code=403, detail='You can only delete your own reports')

    reports_repository.delete_report(db, id)
    return {'message': 'Report deleted successfully'}


def update_report(report: schemas.ReportCreate, id: int, db: Session, user: models.User):
    report_db = reports_repository.get_report_by_id(db, id)
    if not report_db:
        raise HTTPException(status_code=404, detail='Report not found')

    if report_db.user_id != user.id:
        raise HTTPException(status_code=403, detail='You can only update your own reports')

    updated = reports_repository.update_report(db, id, report.model_dump())
    updated.fullname = user.fullname
    return updated


def admin_update_report(report: schemas.ReportCreate, id: int, db: Session, admin: models.Admin):
    report_db = reports_repository.get_report_by_id(db, id)
    if not report_db:
        raise HTTPException(status_code=404, detail='Report not found')

    updated = reports_repository.update_report(db, id, report.model_dump())
    updated.fullname = updated.user.fullname
    return updated


def get_report(id: int, db: Session):
    report = reports_repository.get_report_by_id(db, id)
    if not report:
        raise HTTPException(status_code=404, detail='Report not found')
    report.fullname = report.user.fullname
    return report


def get_reports_by_user_id(id: int, db: Session):
    reports = reports_repository.get_reports_by_user_id(db, id)
    return [schemas.ReportOut(**report.__dict__, fullname=report.user.fullname) for report in reports]


def get_all_reports(db: Session):
    reports = reports_repository.get_all_reports(db)
    return [schemas.ReportOut(**report.__dict__, fullname=report.user.fullname) for report in reports]
