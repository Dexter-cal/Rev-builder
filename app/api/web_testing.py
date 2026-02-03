from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.offensive_tools_service import ProxyService
from app.models import models

router = APIRouter()

@router.post("/capture")
def capture_request(project_id: int, method: str, url: str, db: Session = Depends(get_db)):
    service = ProxyService(db)
    req = service.capture_request(project_id, method, url, {"User-Agent": "Mozilla/5.0"})
    return req

@router.get("/requests/{project_id}")
def get_requests(project_id: int, db: Session = Depends(get_db)):
    service = ProxyService(db)
    return service.get_requests(project_id)

@router.post("/scan")
def start_web_scan(url: str, project_id: int, db: Session = Depends(get_db)):
    # Simulated automated web scanner (ZAP-style)
    finding = models.Finding(
        function_id=None,
        severity="medium",
        confidence=0.8,
        evidence=f"Reflective XSS found at {url}?q=test",
        recommendation="Sanitize all user inputs.",
        risk_score=50
    )
    db.add(finding)
    db.commit()
    return {"message": "Web scan completed", "findings": 1}
