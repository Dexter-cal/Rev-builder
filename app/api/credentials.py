from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import models
from pydantic import BaseModel

router = APIRouter()

class CredentialCreate(BaseModel):
    username: str
    password: str
    type: str
    origin: str

@router.post("/{device_id}")
def add_credential(device_id: int, cred: CredentialCreate, db: Session = Depends(get_db)):
    db_cred = models.Credential(device_id=device_id, **cred.dict())
    db.add(db_cred)
    db.commit()
    return {"message": "Credential stored", "id": db_cred.id}

@router.get("/{device_id}")
def get_credentials(device_id: int, db: Session = Depends(get_db)):
    return db.query(models.Credential).filter(models.Credential.device_id == device_id).all()
