from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.ai_engine_service import AIEngineService
from app.models import models

router = APIRouter()

@router.post("/analyze")
def analyze_code(model_id: int, code: str = Body(...), task: str = "security_audit", db: Session = Depends(get_db)):
    result = AIEngineService.analyze_code(db, model_id, code, task)
    return result

@router.get("/history")
def get_ai_history(db: Session = Depends(get_db)):
    return db.query(models.AIAnalysis).order_by(models.AIAnalysis.created_at.desc()).all()
