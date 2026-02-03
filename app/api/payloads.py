from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.exploit_service import ExploitService
from typing import Optional
import os
import hashlib
from app.models import models

router = APIRouter()

@router.post("/generate")
def generate_payload(finding_id: int, name: str, obfuscation: Optional[str] = "low", db: Session = Depends(get_db)):
    morph_config = {"obfuscation": obfuscation, "encoder": "xor"}
    payload = ExploitService.generate_payload(db, finding_id, name, morph_config)
    if not payload:
        raise HTTPException(status_code=404, detail="Finding not found")
    return {"message": "Payload generated", "payload_id": payload.id, "base_code": payload.base_code}

@router.post("/{payload_id}/morph")
def morph_payload(payload_id: int, db: Session = Depends(get_db)):
    payload = db.query(models.Payload).filter(models.Payload.id == payload_id).first()
    if not payload:
        raise HTTPException(status_code=404, detail="Payload not found")

    code = payload.base_code

    # 1. Variable Renaming (Simulated with simple replace for common shellcode vars)
    vars_to_rename = ['shellcode', 'payload', 'buffer', 'target']
    for v in vars_to_rename:
        new_name = f"var_{os.urandom(4).hex()}"
        code = code.replace(v, new_name)

    # 2. XOR Encoding
    key = os.urandom(1)[0]
    encoded_bytes = []
    # If the payload looks like hex or bytes, we would encode it.
    # For this prototype, we'll append a decoder stub.
    code += f"\n\n# XOR Decoder Stub (Key: {hex(key)})\ndef decode(data, key):\n    return bytes([b ^ key for b in data])\n"

    # 3. Junk code injection
    junk = f"\n# Junk code\n_junk_{os.urandom(2).hex()} = {os.urandom(4).hex()}\n"
    code = junk + code + junk

    variant = models.Variant(
        payload_id=payload_id,
        morph_hash=hashlib.sha256(code.encode()).hexdigest(),
        code=code,
        result="Success"
    )
    db.add(variant)
    db.commit()
    return {"message": "Payload morphed", "variant_id": variant.id, "morphed_code": code}

@router.get("/")
def get_payloads(db: Session = Depends(get_db)):
    return db.query(models.Payload).all()
