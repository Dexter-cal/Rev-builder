from sqlalchemy.orm import Session
from app.models import models
import datetime

class DeploymentService:
    def __init__(self, db: Session):
        self.db = db

    def deploy(self, binary_id: int, target_device_id: int, target_type: str, deployment_path: str):
        binary = self.db.query(models.Binary).filter(models.Binary.id == binary_id).first()
        device = self.db.query(models.Device).filter(models.Device.id == target_device_id).first()

        if not binary or not device:
            return None

        job = models.DeploymentJob(
            binary_id=binary_id,
            target_device_id=target_device_id,
            target_type=target_type,
            deployment_path=deployment_path,
            status="deploying",
            logs=f"Initiating deployment of {binary.path} to {device.name} ({target_type})..."
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        # Simulation logic
        try:
            if target_type == "real":
                job.logs += f"\nEstablishing connection via {device.ip}..."
                job.logs += f"\nPushing binary to {deployment_path}..."
                job.logs += "\nVerifying permissions..."
            elif target_type == "clone":
                job.logs += "\nMounting emulated filesystem..."
                job.logs += f"\nOverwriting {deployment_path} with patched version..."
                job.logs += "\nUnmounting and restarting clone..."
            else:
                job.logs += f"\nSaving copy to {deployment_path}..."

            job.status = "success"
            job.logs += "\nDeployment completed successfully. Application/Software is now live on target."
        except Exception as e:
            job.status = "failed"
            job.logs += f"\nError: {str(e)}"

        self.db.commit()
        return job
