import random
from sqlalchemy.orm import Session
from app.models import models

class BruteforceService:
    def __init__(self, db: Session):
        self.db = db

    def start_job(self, device_id: int, service: str, config: dict):
        job = models.BruteforceJob(
            device_id=device_id,
            service=service,
            status="running",
            config=config
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def run_simulation(self, job_id: int):
        job = self.db.query(models.BruteforceJob).filter(models.BruteforceJob.id == job_id).first()
        if not job:
            return None

        # Common credentials for simulation
        credentials = [
            ("admin", "admin"),
            ("admin", "password123"),
            ("root", "root"),
            ("user", "user")
        ]

        found_success = False
        for user, pwd in credentials:
            success = random.random() < 0.2 # 20% chance of success per attempt
            result = models.BruteforceResult(
                job_id=job.id,
                username=user,
                password=pwd,
                success=success,
                response_code="200" if success else "401"
            )
            self.db.add(result)

            if success:
                found_success = True
                # If success, also create a Credential record
                cred = models.Credential(
                    device_id=job.device_id,
                    username=user,
                    password=pwd,
                    type=job.service,
                    origin=f"Bruteforce Job #{job.id}"
                )
                self.db.add(cred)

                # And create a session
                session = models.Session(
                    device_id=job.device_id,
                    type="shell" if job.service in ["ssh", "telnet"] else "web",
                    info={"IP": "Target IP", "User": user},
                    connected=True
                )
                self.db.add(session)

        job.status = "completed"
        self.db.commit()
        return found_success
