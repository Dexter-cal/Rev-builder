from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models import models
from app.schemas import schemas
from app.services.project_service import ProjectService

router = APIRouter()

@router.get("/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects

@router.post("/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.post("/{project_id}/undo")
def undo_action(project_id: int, db: Session = Depends(get_db)):
    service = ProjectService(db)
    action = service.undo(project_id)
    if not action:
        raise HTTPException(status_code=404, detail="No actions to undo")
    return {"message": "Undone", "action": action}

@router.get("/{project_id}/workflow")
def get_workflow(project_id: int, db: Session = Depends(get_db)):
    service = ProjectService(db)
    return service.get_workflow(project_id)

@router.post("/{project_id}/workflow")
def update_workflow(project_id: int, workflow_data: dict, db: Session = Depends(get_db)):
    service = ProjectService(db)
    return service.update_workflow(project_id, workflow_data.get('nodes', []), workflow_data.get('edges', []))
