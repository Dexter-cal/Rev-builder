from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.visual_code_service import VisualCodeService

router = APIRouter()

@router.get("/graph/{binary_id}")
def get_code_graph(binary_id: int, db: Session = Depends(get_db)):
    service = VisualCodeService(db)
    return service.generate_code_graph(binary_id)

@router.get("/details/{node_id}")
def get_node_details(node_id: str, db: Session = Depends(get_db)):
    service = VisualCodeService(db)
    details = service.touch_node(node_id)
    if not details:
        raise HTTPException(status_code=404, detail="Node details not found")
    return details
