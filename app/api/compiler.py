from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.real_offensive_service import CompilerService
from app.models import models

router = APIRouter()

@router.post("/compile")
def compile_code(project_id: int, source_code: str = Body(...), output_name: str = "custom_tool", db: Session = Depends(get_db)):
    result = CompilerService.compile_c(db, project_id, source_code, output_name)
    return result

@router.get("/binaries/{project_id}")
def list_compiled_binaries(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.Binary).filter(models.Binary.hash == "locally_compiled").all()
