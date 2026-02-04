from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.wordlist_service import WordlistService
from typing import List, Optional

router = APIRouter()

@router.get("/")
def list_wordlists(project_id: Optional[int] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    service = WordlistService(db)
    return service.get_wordlists(project_id, category)

@router.post("/generate")
def generate_wordlist(project_id: int, category: str, context: str, db: Session = Depends(get_db)):
    service = WordlistService(db)
    return service.generate_ai_wordlist(project_id, category, context)

@router.post("/create")
def create_wordlist(name: str, content: str, category: str, project_id: Optional[int] = None, db: Session = Depends(get_db)):
    service = WordlistService(db)
    return service.create_wordlist(name, content, category, project_id)

@router.post("/device-context/{device_id}")
def generate_for_device(device_id: int, db: Session = Depends(get_db)):
    service = WordlistService(db)
    wordlist = service.generate_contextual_bruteforce(device_id)
    if not wordlist:
        raise HTTPException(status_code=404, detail="Device not found")
    return wordlist
