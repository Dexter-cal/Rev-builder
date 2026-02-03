from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import models
from pydantic import BaseModel
from typing import List
import nmap
import json

router = APIRouter()

class AttackSurfaceCreate(BaseModel):
    ip: str
    port: int
    protocol: str
    service: str
    version: str = None
    vuln_info: str = None

@router.post("/{project_id}", response_model=dict)
def add_recon_result(project_id: int, surface: AttackSurfaceCreate, db: Session = Depends(get_db)):
    db_surface = models.AttackSurface(project_id=project_id, **surface.dict())
    db.add(db_surface)
    db.commit()
    return {"message": "Recon result added", "id": db_surface.id}

@router.get("/{project_id}")
def get_recon_results(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.AttackSurface).filter(models.AttackSurface.project_id == project_id).all()

def run_actual_scan(project_id: int, target: str, db_session_factory):
    db = db_session_factory()
    try:
        nm = nmap.PortScanner()
        nm.scan(target, arguments='-sV -T4')

        for host in nm.all_hosts():
            for proto in nm[host].all_protocols():
                lport = nm[host][proto].keys()
                for port in lport:
                    service = nm[host][proto][port]
                    surface = models.AttackSurface(
                        project_id=project_id,
                        ip=host,
                        port=port,
                        protocol=proto,
                        service=service.get('name', 'unknown'),
                        version=service.get('version', 'unknown'),
                        vuln_info=json.dumps(service)
                    )
                    db.add(surface)
        db.commit()
    except Exception as e:
        print(f"Scan error: {e}")
    finally:
        db.close()

@router.post("/{project_id}/scan")
async def trigger_scan(project_id: int, target: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    from app.database.session import SessionLocal
    background_tasks.add_task(run_actual_scan, project_id, target, SessionLocal)
    return {"message": "Scan started in background", "target": target}
