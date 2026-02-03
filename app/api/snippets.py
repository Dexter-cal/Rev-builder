from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import models
from typing import List

router = APIRouter()

@router.get("/")
def list_snippets(category: str = None, db: Session = Depends(get_db)):
    query = db.query(models.CodeSnippet)
    if category:
        query = query.filter(models.CodeSnippet.category == category)
    return query.all()

@router.get("/{snippet_id}")
def get_snippet(snippet_id: int, db: Session = Depends(get_db)):
    snippet = db.query(models.CodeSnippet).filter(models.CodeSnippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return snippet
