from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.hardware_attack_service import HardwareAttackService
from app.models import models

router = APIRouter()

@router.post("/discover/{device_id}")
def discover_interfaces(device_id: int, db: Session = Depends(get_db)):
    service = HardwareAttackService(db)
    return service.discover_interfaces(device_id)

@router.post("/action")
def run_action(device_id: int, interface: str, action: str, db: Session = Depends(get_db)):
    service = HardwareAttackService(db)
    return service.run_hardware_action(device_id, interface, action)

@router.get("/interfaces/{device_id}")
def get_interfaces(device_id: int, db: Session = Depends(get_db)):
    return db.query(models.HardwareInterface).filter(models.HardwareInterface.device_id == device_id).all()

@router.get("/jobs/{device_id}")
def get_jobs(device_id: int, db: Session = Depends(get_db)):
    return db.query(models.HardwareJob).filter(models.HardwareJob.device_id == device_id).all()

@router.get("/suggestions/{device_id}")
def get_suggestions(device_id: int, db: Session = Depends(get_db)):
    service = HardwareAttackService(db)
    return service.get_next_steps(device_id)

@router.get("/payloads/recommendations")
def get_recommendations(arch: str, os: str, db: Session = Depends(get_db)):
    service = HardwareAttackService(db)
    return service.get_recommended_payloads(arch, os)
