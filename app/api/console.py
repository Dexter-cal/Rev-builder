from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.console_service import ConsoleService
from pydantic import BaseModel

router = APIRouter()

# Global state for prototype
sessions = {}

class CommandRequest(BaseModel):
    session_id: str
    command: str

@router.post("/execute")
def execute_console_command(req: CommandRequest, db: Session = Depends(get_db)):
    if req.session_id not in sessions:
        sessions[req.session_id] = ConsoleService(db)

    svc = sessions[req.session_id]
    svc.db = db # Refresh DB session
    output = svc.execute_command(req.command)

    return {
        "output": output,
        "prompt": f"offsec({svc.active_module.name if svc.active_module else ''}) > "
    }

@router.post("/init")
def init_console():
    import uuid
    session_id = str(uuid.uuid4())
    return {"session_id": session_id, "prompt": "offsec > "}
