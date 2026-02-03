from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.analysis_service import AnalysisService
from app.models import models
import hashlib
import os
import shutil
from typing import Optional

router = APIRouter()

@router.post("/ingest")
def ingest_binary(device_id: int, path: str, db: Session = Depends(get_db)):
    binary = AnalysisService.simulate_binary_ingestion(db, device_id, path)
    return {"message": "Binary ingested", "binary_id": binary.id, "functions": len(binary.functions)}

@router.post("/scan/{binary_id}")
def scan_binary(binary_id: int, db: Session = Depends(get_db)):
    findings_count = AnalysisService.scan_binary(db, binary_id)
    if findings_count is None:
        raise HTTPException(status_code=404, detail="Binary not found")
    return {"message": "Scan complete", "findings_created": findings_count}

@router.post("/upload")
async def upload_binary(
    project_id: int = Form(...),
    device_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    # Simple extension-based type detection for prototype
    ext = file.filename.split('.')[-1].lower()
    file_type = "UNKNOWN"
    arch = "x86_64" # Default

    if ext == 'exe': file_type = "PE (Windows Executable)"
    elif ext == 'apk': file_type = "APK (Android Package)"; arch = "ARM"
    elif ext in ['elf', 'bin']: file_type = "ELF (Linux/Embedded)"
    elif ext == 'firmware': file_type = "Firmware Image"

    # Create binary entry
    binary = models.Binary(
        device_id=device_id,
        path=file.filename,
        hash=file_hash,
        arch=arch,
        file_type=file_type,
        size=len(content)
    )
    db.add(binary)
    db.commit()
    db.refresh(binary)

    # Save file and analyze if ELF
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{binary.id}_{file.filename}")

    with open(temp_path, "wb") as buffer:
        buffer.write(content)

    if "ELF" in file_type:
        AnalysisService.analyze_elf(db, binary.id, temp_path)
    else:
        # Fallback to simulation for non-ELF
        functions_data = [
            {
                "name": "simulated_func",
                "offset": "0x401000",
                "size": 128,
                "assembly_snippet": "push rbp; mov rbp, rsp; call gets; leave; ret",
                "python_like": "def main():\n    gets(buffer)",
                "danger_score": 90,
                "vuln_type": "buffer_overflow"
            }
        ]
        for func_data in functions_data:
            function = models.Function(binary_id=binary.id, **func_data)
            db.add(function)
        db.commit()
    db.refresh(binary)

    return {
        "message": "File uploaded and analyzed",
        "binary_id": binary.id,
        "filename": file.filename,
        "hash": file_hash,
        "type": file_type,
        "functions": [
            {
                "name": f.name,
                "offset": f.offset,
                "python_like": f.python_like,
                "assembly_snippet": f.assembly_snippet
            } for f in binary.functions
        ]
    }

@router.post("/break/{function_id}")
def try_to_break(function_id: int, db: Session = Depends(get_db)):
    function = db.query(models.Function).filter(models.Function.id == function_id).first()
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")

    binary = function.binary
    device_id = binary.device_id if binary else None

    # Create a simulated session if we have a device
    if device_id:
        session = models.Session(
            device_id=device_id,
            type="shell",
            info={"OS": "Linux", "user": "root", "IP": "192.168.1.1"},
            connected=True
        )
        db.add(session)
        db.commit()

    # Simulate exploit process
    return {
        "logs": [
            f"Attempting to break function '{function.name}' at {function.offset}...",
            "[+] Analyzing stack layout...",
            f"[+] Found potential {function.vuln_type} overflow",
            "[+] Generating ROP chain...",
            "[!] Payload sent: (128 bytes padding) + (ROP gadget) + (shellcode)",
            "[*] Exploit successful! Shell opened.",
            "root@target-device:/# "
        ],
        "success": True
    }

@router.post("/explain/{function_id}")
def explain_function(function_id: int, db: Session = Depends(get_db)):
    function = db.query(models.Function).filter(models.Function.id == function_id).first()
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")

    explanation = f"AI Explanation for '{function.name}':\n"
    explanation += "This function appears to handle user input without proper bounds checking. "
    explanation += "Specifically, the use of 'gets' (or equivalent assembly pattern) at the offset allows an attacker to overwrite the return address on the stack. "
    explanation += "This could lead to arbitrary code execution or a Denial of Service."

    return {"explanation": explanation}
