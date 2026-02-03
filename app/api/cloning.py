from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.cloning_service import CloningService
from app.models import models

router = APIRouter()

@router.post("/start")
def start_cloning(project_id: int, channel: str, source_info: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    service = CloningService(db)
    job = service.create_job(project_id, channel, source_info)
    background_tasks.add_task(service.run_cloning, job.id, f"cloned_{channel}_{project_id}.bin")
    return {"message": "Cloning job started", "job_id": job.id}

@router.get("/jobs/{project_id}")
def get_jobs(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.CloningJob).filter(models.CloningJob.project_id == project_id).all()
