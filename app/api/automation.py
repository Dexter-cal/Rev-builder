from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import models

router = APIRouter()

@router.post("/trigger")
def trigger_automation(event_type: str, context: dict = Body(...), db: Session = Depends(get_db)):
    # Simulated automation engine
    # In a real tool, this would look up scripts in the DB and run them
    logs = [f"Automation triggered by event: {event_type}"]

    if event_type == "new_finding":
        logs.append(f"Auto-analyzing finding #{context.get('finding_id')} with default AI model...")
        logs.append("[+] Automation: AI analysis requested and stored.")

    return {"status": "success", "logs": logs}

@router.get("/rules")
def list_rules(db: Session = Depends(get_db)):
    # Placeholder for automation rules
    return [
        {"id": 1, "event": "new_finding", "action": "ai_analyze", "enabled": True},
        {"id": 2, "event": "new_device", "action": "nmap_scan", "enabled": False}
    ]
