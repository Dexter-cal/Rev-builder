from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.decompilation_service import DecompilationService
from app.models import models

router = APIRouter()

@router.post("/{binary_id}")
def decompile_binary(binary_id: int, db: Session = Depends(get_db)):
    service = DecompilationService(db)
    job = service.decompile(binary_id)
    if not job:
        raise HTTPException(status_code=404, detail="Binary not found")
    return job

@router.get("/jobs/{binary_id}")
def get_jobs(binary_id: int, db: Session = Depends(get_db)):
    return db.query(models.DecompilationJob).filter(models.DecompilationJob.binary_id == binary_id).all()
