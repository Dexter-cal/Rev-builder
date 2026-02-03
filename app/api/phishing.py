from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.offensive_tools_service import PhishingService
from app.models import models

router = APIRouter()

@router.post("/campaigns")
def create_campaign(project_id: int, name: str, template: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    service = PhishingService(db)
    campaign = service.create_campaign(project_id, name, template)
    background_tasks.add_task(service.simulate_activity, campaign.id)
    return campaign

@router.get("/campaigns/{project_id}")
def get_campaigns(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.PhishingCampaign).filter(models.PhishingCampaign.project_id == project_id).all()
