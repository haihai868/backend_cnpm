from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models, security
from app.database_connect import get_db

router = APIRouter(
    prefix='/reports',
    tags=['reports']
)

@router.post('/', status_code=201, response_model=schemas.ReportOut)
def create_report(report: schemas.ReportCreate, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    report = models.Report(**report.model_dump(), user_id=user.id)
    db.add(report)
    db.commit()
    db.refresh(report)

    report.fullname = user.fullname
    return report

@router.delete('/{id}')
def delete_report(id: int, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    report = db.query(models.Report).filter(models.Report.id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.user_id != user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own reports")

    db.delete(report)
    db.commit()
    return {'message': 'Report deleted successfully'}


@router.put('/{id}', response_model=schemas.ReportOut)
def update_report(report: schemas.ReportCreate, id: int, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    report_db = db.query(models.Report).filter(models.Report.id == id).first()
    if not report_db:
        raise HTTPException(status_code=404, detail="Report not found")

    if report_db.user_id != user.id:
        raise HTTPException(status_code=403, detail="You can only update your own reports")

    report_db.message = report.message
    db.commit()
    db.refresh(report_db)
    report_db.fullname = user.fullname
    return report_db

@router.get('/{id}', response_model=schemas.ReportOut)
def get_report(id: int, db: Session = Depends(get_db)):
    report = db.query(models.Report).filter(models.Report.id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.fullname = report.user.fullname
    return report

@router.get('/', response_model=List[schemas.ReportOut])
def get_all_reports(db: Session = Depends(get_db)):
    reports = db.query(models.Report).all()

    reports = [schemas.ReportOut(**report.__dict__, fullname=report.user.fullname) for report in reports]
    return reports
