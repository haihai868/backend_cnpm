from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models, security
from app.services import reports_service
from app.database_connect import get_db

router = APIRouter(
    prefix='/reports',
    tags=['reports']
)

@router.post('/', status_code=201, response_model=schemas.ReportOut)
def create_report(report: schemas.ReportCreate, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    return reports_service.create_report(report, db, user)

@router.delete('/{id}')
def delete_report(id: int, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    return reports_service.delete_report(id, db, user)


@router.put('/{id}', response_model=schemas.ReportOut)
def update_report(report: schemas.ReportCreate, id: int, db: Session = Depends(get_db), user: models.User = Depends(security.get_current_user)):
    return reports_service.update_report(report, id, db, user)

@router.put('/admin/{id}', response_model=schemas.ReportOut)
def admin_update_report(report: schemas.ReportCreate, id: int, db: Session = Depends(get_db), admin: models.Admin = Depends(security.get_current_admin)):
    return reports_service.admin_update_report(report, id, db, admin)

@router.get('/{id}', response_model=schemas.ReportOut)
def get_report(id: int, db: Session = Depends(get_db)):
    return reports_service.get_report(id, db)

@router.get('/users/{id}', response_model=List[schemas.ReportOut])
def get_reports_by_user_id(id: int, db: Session = Depends(get_db)):
    return reports_service.get_reports_by_user_id(id, db)

@router.get('/', response_model=List[schemas.ReportOut])
def get_all_reports(db: Session = Depends(get_db)):
    return reports_service.get_all_reports(db)
