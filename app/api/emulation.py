from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.advanced_security_service import AdvancedSecurityService
from app.models import models

router = APIRouter()

@router.post("/start")
def start_emulation(binary_id: int, engine: str = "unicorn", db: Session = Depends(get_db)):
    service = AdvancedSecurityService(db)
    return service.run_emulation(binary_id, engine)

@router.get("/jobs/{binary_id}")
def get_jobs(binary_id: int, db: Session = Depends(get_db)):
    return db.query(models.EmulationJob).filter(models.EmulationJob.binary_id == binary_id).all()
