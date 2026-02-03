import os
import shutil
import hashlib
from sqlalchemy.orm import Session
from app.models import models
from app.services.asset_service import AssetService

class CloningService:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, project_id: int, channel: str, source_info: str):
        job = models.CloningJob(
            project_id=project_id,
            channel=channel,
            source_info=source_info,
            status="pending"
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def run_cloning(self, job_id: int, filename: str = "cloned_artifact.bin"):
        job = self.db.query(models.CloningJob).filter(models.CloningJob.id == job_id).first()
        if not job:
            return None

        job.status = "cloning"
        self.db.commit()

        # Simulate cloning process
        # Create a dummy artifact file
        artifact_content = b"\x7fELF" + os.urandom(1024)
        artifact_hash = hashlib.sha256(artifact_content).hexdigest()

        # Save to storage using AssetService
        # For simplicity, we create a device first if none exists for this project
        device = self.db.query(models.Device).filter(models.Device.project_id == job.project_id).first()
        if not device:
            device = models.Device(
                project_id=job.project_id,
                name=f"Cloned-Device-{job.channel}",
                type="cloned"
            )
            self.db.add(device)
            self.db.commit()
            self.db.refresh(device)

        # Register as a Binary
        binary = models.Binary(
            device_id=device.id,
            path=f"/cloned/{filename}",
            hash=artifact_hash,
            arch="x86_64",
            file_type="ELF",
            size=len(artifact_content)
        )
        self.db.add(binary)
        self.db.commit()
        self.db.refresh(binary)

        # Write the file to disk
        file_path = AssetService.save_asset(job.project_id, "binaries", filename, artifact_content)

        job.binary_id = binary.id
        job.status = "completed"
        self.db.commit()
        return binary
