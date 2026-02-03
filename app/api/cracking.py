from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.offensive_tools_service import CrackingService
from app.models import models

router = APIRouter()

@router.post("/jobs")
def start_cracking(project_id: int, hash_type: str, hashes: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    service = CrackingService(db)
    hash_list = hashes.split(",")
    job = service.start_job(project_id, hash_type, hash_list)
    background_tasks.add_task(service.run_simulation, job.id)
    return job

@router.get("/jobs/{project_id}")
def get_jobs(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.CrackingJob).filter(models.CrackingJob.project_id == project_id).all()
