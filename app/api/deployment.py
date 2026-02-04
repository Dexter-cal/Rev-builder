from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.deployment_service import DeploymentService
from app.models import models

router = APIRouter()

@router.post("/")
def deploy_binary(
    binary_id: int,
    target_device_id: int,
    target_type: str = Query("real", enum=["real", "clone", "copy"]),
    deployment_path: str = "/tmp/patched_binary",
    db: Session = Depends(get_db)
):
    service = DeploymentService(db)
    job = service.deploy(binary_id, target_device_id, target_type, deployment_path)
    if not job:
        raise HTTPException(status_code=404, detail="Binary or Device not found")
    return job

@router.get("/history")
def get_deployment_history(db: Session = Depends(get_db)):
    return db.query(models.DeploymentJob).order_by(models.DeploymentJob.created_at.desc()).all()
