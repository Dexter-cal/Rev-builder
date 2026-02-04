from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.real_offensive_service import CompilerService, ExecutionService
from app.services.firmware_service import FirmwareService
from app.models import models

router = APIRouter()

@router.post("/compile")
def compile_code(project_id: int, source_code: str = Body(...), output_name: str = "custom_tool", db: Session = Depends(get_db)):
    result = CompilerService.compile_c(db, project_id, source_code, output_name)
    return result

@router.post("/run")
def run_code(project_id: int, language: str, source_code: str = Body(...), binary_id: int = None, db: Session = Depends(get_db)):
    if language == "python":
        return ExecutionService.run_python(source_code)
    elif language == "c":
        # If binary_id provided, run that, otherwise compile and run
        if binary_id:
            binary = db.query(models.Binary).filter(models.Binary.id == binary_id).first()
            if not binary: raise HTTPException(status_code=404, detail="Binary not found")
            return ExecutionService.run_binary(binary.path)
        else:
            comp = CompilerService.compile_c(db, project_id, source_code, "temp_run")
            if comp["success"]:
                return ExecutionService.run_binary(comp["binary_path"])
            else:
                return {"error": "Compilation failed", "logs": comp["logs"]}
    else:
        raise HTTPException(status_code=400, detail="Unsupported language")

@router.get("/binaries/{project_id}")
def list_compiled_binaries(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.Binary).filter(models.Binary.hash == "locally_compiled").all()

@router.post("/recompile/create")
def create_recompilation_job(project_id: int, binary_id: int, source_code: str = Body(...), target_arch: str = "arm", db: Session = Depends(get_db)):
    service = FirmwareService(db)
    return service.create_recompilation_job(project_id, binary_id, source_code, target_arch)

@router.post("/recompile/run/{job_id}")
def run_recompilation(job_id: int, db: Session = Depends(get_db)):
    service = FirmwareService(db)
    return service.run_recompilation(job_id)

@router.get("/recompile/jobs/{project_id}")
def get_recompilation_jobs(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.RecompilationJob).filter(models.RecompilationJob.project_id == project_id).all()
