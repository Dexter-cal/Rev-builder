from sqlalchemy.orm import Session
from app.models import models
import json

class ProxyService:
    def __init__(self, db: Session):
        self.db = db

    def capture_request(self, project_id: int, method: str, url: str, headers: dict, body: str = None):
        request = models.WebProxyRequest(
            project_id=project_id,
            method=method,
            url=url,
            headers=headers,
            body=body,
            response_code=200, # Simulated
            response_body="<html>Success</html>" # Simulated
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def get_requests(self, project_id: int):
        return self.db.query(models.WebProxyRequest).filter(models.WebProxyRequest.project_id == project_id).all()

class PhishingService:
    def __init__(self, db: Session):
        self.db = db

    def create_campaign(self, project_id: int, name: str, template: str):
        campaign = models.PhishingCampaign(
            project_id=project_id,
            name=name,
            template=template,
            status="active"
        )
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def simulate_activity(self, campaign_id: int):
        campaign = self.db.query(models.PhishingCampaign).filter(models.PhishingCampaign.id == campaign_id).first()
        if not campaign:
            return None

        campaign.clicks += 5
        campaign.submissions += 2

        # If submissions found, create credentials
        for i in range(2):
            cred = models.Credential(
                device_id=None,
                username=f"victim_{i}@target.com",
                password=f"p@ssword{i}",
                type="phished",
                origin=f"Phishing Campaign: {campaign.name}"
            )
            self.db.add(cred)

        self.db.commit()
        return campaign

class CrackingService:
    def __init__(self, db: Session):
        self.db = db

    def start_job(self, project_id: int, hash_type: str, hashes: list):
        job = models.CrackingJob(
            project_id=project_id,
            hash_type=hash_type,
            hashes=hashes,
            status="running",
            results={}
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def run_simulation(self, job_id: int):
        job = self.db.query(models.CrackingJob).filter(models.CrackingJob.id == job_id).first()
        if not job:
            return None

        # Simulated cracked results
        cracked = {h: "password123" for h in job.hashes[:2]}
        job.results = cracked
        job.status = "completed"

        # Add to credentials
        for h, p in cracked.items():
            cred = models.Credential(
                device_id=None,
                username=f"hash_{h[:8]}",
                password=p,
                type="cracked",
                origin=f"Cracking Job: {job.id}"
            )
            self.db.add(cred)

        self.db.commit()
        return job
