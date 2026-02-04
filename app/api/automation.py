from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.automation_service import AutomationService

router = APIRouter()

@router.get("/triggers/{project_id}")
def list_triggers(project_id: int, db: Session = Depends(get_db)):
    service = AutomationService(db)
    return service.list_triggers(project_id)

@router.post("/pipeline/run")
def run_pipeline(project_id: int, name: str, db: Session = Depends(get_db)):
    service = AutomationService(db)
    return service.run_pipeline(project_id, name)
