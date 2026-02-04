from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.emulation_service import EmulationService
from app.models import models

router = APIRouter()

@router.post("/start")
def start_emulation(binary_id: int, engine: str = "unicorn", db: Session = Depends(get_db)):
    service = EmulationService(db)
    return service.run_emulation(binary_id, engine)

@router.post("/clone-and-emulate")
def clone_and_emulate(device_id: int, firmware_id: int, db: Session = Depends(get_db)):
    service = EmulationService(db)
    return service.clone_and_emulate(device_id, firmware_id)

@router.get("/jobs/{binary_id}")
def get_jobs(binary_id: int, db: Session = Depends(get_db)):
    return db.query(models.EmulationJob).filter(models.EmulationJob.binary_id == binary_id).all()
