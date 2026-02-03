from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.intelligence_service import IntelligenceService
from typing import List

router = APIRouter()

@router.get("/suggestions/{finding_id}")
def get_suggestions(finding_id: int, db: Session = Depends(get_db)):
    service = IntelligenceService(db)
    return service.get_suggestions(finding_id)

@router.post("/chain-builder")
def build_chain(finding_ids: List[int], name: str = "Automated Chain", db: Session = Depends(get_db)):
    service = IntelligenceService(db)
    if not finding_ids:
        raise HTTPException(status_code=400, detail="No finding IDs provided")
    return service.build_exploit_chain(finding_ids, name)

@router.post("/analyze-binary/{binary_id}")
def analyze_binary(binary_id: int, db: Session = Depends(get_db)):
    service = IntelligenceService(db)
    protections = service.analyze_binary_protections(binary_id)
    return {"binary_id": binary_id, "protections": protections}
