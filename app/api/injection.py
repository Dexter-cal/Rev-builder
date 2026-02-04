from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.injection_service import InjectionService

router = APIRouter()

@router.get("/cheat-sheet")
def get_cheat_sheet(category: str = None, db: Session = Depends(get_db)):
    service = InjectionService(db)
    return service.get_cheat_sheet(category)

@router.post("/seed")
def seed_snippets(db: Session = Depends(get_db)):
    service = InjectionService(db)
    service.seed_default_snippets()
    return {"message": "Snippets seeded"}
