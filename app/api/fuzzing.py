from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.fuzzing_service import FuzzingService
from app.models import models

router = APIRouter()

@router.post("/start")
def start_fuzzing(binary_id: int, background_tasks: BackgroundTasks, target_function_id: int = None, db: Session = Depends(get_db)):
    service = FuzzingService(db)
    config = {"engine": "simulated", "timeout": 300}
    job = service.start_fuzzing(binary_id, config, target_function_id)
    background_tasks.add_task(service.run_simulation, job.id)
    return {"message": "Fuzzing job started", "job_id": job.id}

@router.get("/jobs/{binary_id}")
def get_jobs(binary_id: int, db: Session = Depends(get_db)):
    return db.query(models.FuzzingJob).filter(models.FuzzingJob.binary_id == binary_id).all()

@router.get("/results/{job_id}")
def get_results(job_id: int, db: Session = Depends(get_db)):
    return db.query(models.FuzzingResult).filter(models.FuzzingResult.job_id == job_id).all()
