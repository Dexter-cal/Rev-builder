from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.advanced_security_service import HardwareInterfaceService
from app.models import models

router = APIRouter()

@router.post("/action")
def run_action(device_id: int, interface: str, action: str, db: Session = Depends(get_db)):
    service = HardwareInterfaceService(db)
    return service.run_hardware_action(device_id, interface, action)

@router.get("/jobs/{device_id}")
def get_jobs(device_id: int, db: Session = Depends(get_db)):
    return db.query(models.HardwareJob).filter(models.HardwareJob.device_id == device_id).all()
