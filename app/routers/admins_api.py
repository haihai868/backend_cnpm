from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models, security
from app.database_connect import get_db

router = APIRouter(
    prefix='/admins',
    tags=['admins']
)

@router.post('/', response_model=schemas.AdminOut)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    query = db.query(models.Admin).filter(models.Admin.email == admin.email)
    if query.first():
        raise HTTPException(status_code=400, detail='Email already registered')

    admin.password = security.hash(admin.password)
    new_admin = models.Admin(**admin.model_dump())
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

@router.get('/{id}', response_model=schemas.AdminOut)
def get_admin(id: int, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.id == id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return admin

@router.post('/password-verification/{password}')
def verify_password(password: str, admin: models.Admin = Depends(security.get_current_admin)):
    if security.verify(password, admin.password):
        return {'message': 'Password is correct'}
    raise HTTPException(status_code=403, detail='Incorrect password')

@router.put('/', response_model=schemas.AdminOut)
def update_admin(updated_admin: schemas.AdminCreate, db: Session = Depends(get_db), admin: models.Admin = Depends(security.get_current_admin)):
    admin_query = db.query(models.Admin).filter(models.Admin.id == admin.id)
    updated_admin.password = security.hash(updated_admin.password)
    admin_query.update(updated_admin.model_dump(), synchronize_session=False)
    db.commit()
    return admin_query.first()

