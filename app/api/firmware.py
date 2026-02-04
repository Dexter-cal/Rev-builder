from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.firmware_service import FirmwareService
from app.models import models

router = APIRouter()

@router.post("/register")
def register_firmware(device_id: int, file_path: str, version: str = "1.0.0", db: Session = Depends(get_db)):
    service = FirmwareService(db)
    return service.register_firmware(device_id, file_path, version)

@router.post("/extract/{firmware_id}")
def extract_firmware(firmware_id: int, db: Session = Depends(get_db)):
    service = FirmwareService(db)
    path = service.extract_firmware(firmware_id)
    if not path:
        raise HTTPException(status_code=404, detail="Firmware not found")
    return {"message": "Extraction complete", "path": path}

@router.post("/analyze/{firmware_id}")
def analyze_firmware(firmware_id: int, tool: str, db: Session = Depends(get_db)):
    service = FirmwareService(db)
    analysis = service.run_analysis(firmware_id, tool)
    if not analysis:
        raise HTTPException(status_code=404, detail="Firmware not found")
    return analysis

@router.get("/images/{device_id}")
def get_firmware_images(device_id: int, db: Session = Depends(get_db)):
    return db.query(models.FirmwareImage).filter(models.FirmwareImage.device_id == device_id).all()

@router.get("/analysis/{firmware_id}")
def get_analysis_results(firmware_id: int, db: Session = Depends(get_db)):
    return db.query(models.FirmwareAnalysis).filter(models.FirmwareAnalysis.firmware_id == firmware_id).all()
