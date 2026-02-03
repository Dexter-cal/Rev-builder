from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import models
from elftools.elf.elffile import ELFFile
import os

router = APIRouter()

@router.post("/diff")
def diff_binaries(binary_a_id: int, binary_b_id: int, db: Session = Depends(get_db)):
    bin_a = db.query(models.Binary).filter(models.Binary.id == binary_a_id).first()
    bin_b = db.query(models.Binary).filter(models.Binary.id == binary_b_id).first()

    if not bin_a or not bin_b:
        raise HTTPException(status_code=404, detail="One or both binaries not found")

    # Simple function-level diff simulation
    # In a real tool, we would compare CFGs or instruction deltas
    funcs_a = {f.name: f for f in bin_a.functions}
    funcs_b = {f.name: f for f in bin_b.functions}

    added = [name for name in funcs_b if name not in funcs_a]
    removed = [name for name in funcs_a if name not in funcs_b]
    modified = []

    for name in funcs_a:
        if name in funcs_b:
            if funcs_a[name].size != funcs_b[name].size or funcs_a[name].hash != funcs_b[name].hash:
                modified.append({
                    "name": name,
                    "old_size": funcs_a[name].size,
                    "new_size": funcs_b[name].size,
                    "risk_increase": funcs_b[name].danger_score > funcs_a[name].danger_score
                })

    diff_data = {
        "added_functions": added,
        "removed_functions": removed,
        "modified_functions": modified,
        "summary": f"Diff complete: {len(added)} added, {len(removed)} removed, {len(modified)} modified."
    }

    diff_record = models.FirmwareDiff(
        binary_a_id=binary_a_id,
        binary_b_id=binary_b_id,
        diff_data=diff_data
    )
    db.add(diff_record)
    db.commit()
    db.refresh(diff_record)

    return diff_record

@router.get("/{binary_id}/history")
def get_diff_history(binary_id: int, db: Session = Depends(get_db)):
    return db.query(models.FirmwareDiff).filter(
        (models.FirmwareDiff.binary_a_id == binary_id) | (models.FirmwareDiff.binary_b_id == binary_id)
    ).all()
