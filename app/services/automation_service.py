from sqlalchemy.orm import Session
from app.models import models
import datetime

class AutomationService:
    def __init__(self, db: Session):
        self.db = db

    def create_trigger(self, project_id: int, event: str, action: str, config: dict):
        trigger = models.AutomationTrigger(
            project_id=project_id,
            event_type=event,
            action_type=action,
            config=config
        )
        self.db.add(trigger)
        self.db.commit()
        return trigger

    def list_triggers(self, project_id: int):
        return self.db.query(models.AutomationTrigger).filter(
            models.AutomationTrigger.project_id == project_id
        ).all()

    def run_pipeline(self, project_id: int, pipeline_name: str):
        """Simulates running a CI-style security testing pipeline."""
        logs = [
            f"[{datetime.datetime.now()}] Starting pipeline: {pipeline_name}",
            "[*] Step 1: Checking for new firmware dumps...",
            "[*] Step 2: Running Binwalk on eagle_eye_v1.bin",
            "[*] Step 3: Fuzzing handle_notification symbol...",
            "[*] Step 4: Generating interim report.",
            f"[+] Pipeline {pipeline_name} completed successfully."
        ]
        return {"status": "success", "logs": logs}
