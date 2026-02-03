from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import models
from app.services.asset_service import AssetService
import os
import re

router = APIRouter()

@router.post("/upload")
async def upload_source(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await file.read()
    file_path = AssetService.save_asset(project_id, "source", file.filename, content)

    return {"message": "Source file uploaded", "path": file_path}

@router.post("/audit/{project_id}")
def audit_source(project_id: int, db: Session = Depends(get_db)):
    source_dir = os.path.join(AssetService.get_project_dir(project_id), "source")
    if not os.path.exists(source_dir):
        return {"message": "No source files found", "findings": []}

    findings = []
    unsafe_patterns = [
        (r"gets\(", "Use of unsafe function 'gets' (Buffer Overflow risk)"),
        (r"strcpy\(", "Use of unsafe function 'strcpy' (Buffer Overflow risk)"),
        (r"system\(", "Use of 'system()' call (Command Injection risk)"),
        (r"password\s*=\s*['\"].*['\"]", "Potentially hardcoded password found"),
        (r"api_key\s*=\s*['\"].*['\"]", "Potentially hardcoded API key found")
    ]

    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r", errors="ignore") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    for pattern, desc in unsafe_patterns:
                        if re.search(pattern, line):
                            findings.append({
                                "file": filename,
                                "line": i + 1,
                                "match": line.strip(),
                                "description": desc
                            })

    return {
        "project_id": project_id,
        "files_scanned": len(os.listdir(source_dir)),
        "findings_count": len(findings),
        "findings": findings
    }
