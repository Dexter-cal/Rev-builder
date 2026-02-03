from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.bruteforce_service import BruteforceService
from app.models import models

router = APIRouter()

@router.post("/start")
def start_bruteforce(device_id: int, service_name: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    service = BruteforceService(db)
    config = {"wordlist": "default_passwords.txt", "threads": 4}
    job = service.start_job(device_id, service_name, config)
    background_tasks.add_task(service.run_simulation, job.id)
    return {"message": "Bruteforce job started", "job_id": job.id}

@router.get("/jobs/{device_id}")
def get_jobs(device_id: int, db: Session = Depends(get_db)):
    return db.query(models.BruteforceJob).filter(models.BruteforceJob.device_id == device_id).all()

@router.get("/results/{job_id}")
def get_results(job_id: int, db: Session = Depends(get_db)):
    return db.query(models.BruteforceResult).filter(models.BruteforceResult.job_id == job_id).all()
