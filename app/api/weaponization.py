from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.advanced_security_service import AdvancedSecurityService
from app.services.real_offensive_service import WeaponizerService
from app.models import models

router = APIRouter()

@router.post("/weaponize")
def weaponize(finding_id: int, project_id: int, platform: str, exploit_type: str, db: Session = Depends(get_db)):
    # Use real weaponizer
    weapon = WeaponizerService.generate_real_exploit(db, finding_id, project_id)
    if not weapon:
        raise HTTPException(status_code=404, detail="Finding not found")
    return weapon

@router.get("/jobs/{finding_id}")
def get_jobs(finding_id: int, db: Session = Depends(get_db)):
    return db.query(models.WeaponizationJob).filter(models.WeaponizationJob.finding_id == finding_id).all()
