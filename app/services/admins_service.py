from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.repositories import admins_repository


def create_admin(admin: schemas.AdminCreate, db: Session):
    if admins_repository.get_admin_by_email(db, admin.email):
        raise HTTPException(status_code=400, detail='Email already registered')
    admin.password = security.hash(admin.password)
    return admins_repository.create_admin(db, admin.model_dump())


def get_admin(id: int, db: Session):
    admin = admins_repository.get_admin_by_id(db, id)
    if not admin:
        raise HTTPException(status_code=404, detail='Admin not found')
    return admin


def verify_password(password: str, admin: models.Admin):
    if security.verify(password, admin.password):
        return {'message': 'Password is correct'}
    raise HTTPException(status_code=403, detail='Incorrect password')


def update_admin(updated_admin: schemas.AdminCreate, db: Session, admin: models.Admin):
    updated_admin.password = security.hash(updated_admin.password)
    return admins_repository.update_admin(db, admin.id, updated_admin.model_dump())
