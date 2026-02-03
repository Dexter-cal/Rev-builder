from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.advanced_security_service import SettingsService
from app.models import models
from typing import List

router = APIRouter()

@router.get("/ai-models")
def get_ai_models(db: Session = Depends(get_db)):
    return db.query(models.AIModel).all()

@router.post("/ai-models/{model_id}")
def update_ai_model(model_id: int, config: dict, db: Session = Depends(get_db)):
    service = SettingsService(db)
    model = service.update_ai_model(model_id, config)
    if not model:
        raise HTTPException(status_code=404, detail="AI Model not found")
    return model

@router.get("/config")
def get_all_configs(db: Session = Depends(get_db)):
    return db.query(models.SystemConfig).all()

@router.post("/config")
def set_config(key: str, value: dict, description: str = "", db: Session = Depends(get_db)):
    service = SettingsService(db)
    return service.set_system_config(key, value, description)

@router.get("/packages")
def list_packages():
    import subprocess
    import sys
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=json"], capture_output=True, text=True)
        import json
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}

@router.post("/packages/install")
def install_package(package: str):
    import subprocess
    import sys
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return {"message": f"Successfully installed {package}"}
    except Exception as e:
        return {"error": str(e)}
