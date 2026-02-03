from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import models
from app.services.asset_service import AssetService
import os

router = APIRouter()

@router.post("/extract/{binary_id}")
def extract_firmware(binary_id: int, db: Session = Depends(get_db)):
    binary = db.query(models.Binary).filter(models.Binary.id == binary_id).first()
    if not binary:
        raise HTTPException(status_code=404, detail="Binary not found")

    project_id = binary.device.project_id

    # Simulation: Extraction logic
    extracted_files = [
        "etc/passwd",
        "etc/shadow",
        "bin/busybox",
        "usr/lib/libnvram.so",
        "init"
    ]

    results = []
    for file_path in extracted_files:
        # Save simulated content
        filename = file_path.replace("/", "_")
        full_path = AssetService.save_asset(
            project_id,
            "firmware_extracted",
            f"ext_{binary.id}_{filename}",
            f"Simulated content for {file_path}".encode()
        )
        results.append({"original_path": file_path, "stored_path": full_path})

    return {
        "message": "Firmware extraction complete",
        "binary": binary.path,
        "extracted_count": len(results),
        "files": results
    }
