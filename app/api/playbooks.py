from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.playbook_service import PlaybookService

router = APIRouter()

@router.get("/")
def get_playbooks(category: str = None, db: Session = Depends(get_db)):
    service = PlaybookService(db)
    return service.get_playbooks(category)

@router.post("/threat-model/{project_id}")
def generate_threat_model(project_id: int, db: Session = Depends(get_db)):
    service = PlaybookService(db)
    return service.generate_threat_model(project_id)
