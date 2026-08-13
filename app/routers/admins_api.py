from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models, security
from app.services import admins_service
from app.database_connect import get_db

router = APIRouter(
    prefix='/admins',
    tags=['admins']
)

@router.post('/',status_code=201, response_model=schemas.AdminOut)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    return admins_service.create_admin(admin, db)

@router.get('/{id}', response_model=schemas.AdminOut)
def get_admin(id: int, db: Session = Depends(get_db)):
    return admins_service.get_admin(id, db)

@router.post('/password-verification/{password}')
def verify_password(password: str, admin: models.Admin = Depends(security.get_current_admin)):
    return admins_service.verify_password(password, admin)

@router.put('/', response_model=schemas.AdminOut)
def update_admin(updated_admin: schemas.AdminCreate, db: Session = Depends(get_db), admin: models.Admin = Depends(security.get_current_admin)):
    return admins_service.update_admin(updated_admin, db, admin)

