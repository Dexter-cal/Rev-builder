from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.collaboration_service import CollaborationService

router = APIRouter()

@router.get("/collaborators/{project_id}")
def get_collaborators(project_id: int, db: Session = Depends(get_db)):
    service = CollaborationService(db)
    return service.get_online_collaborators(project_id)

@router.post("/comment")
def add_comment(node_id: int, user_id: int, content: str, db: Session = Depends(get_db)):
    service = CollaborationService(db)
    return service.add_comment(node_id, user_id, content)

@router.get("/comments/{node_id}")
def get_comments(node_id: int, db: Session = Depends(get_db)):
    service = CollaborationService(db)
    return service.get_comments(node_id)
