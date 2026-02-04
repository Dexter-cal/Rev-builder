from sqlalchemy.orm import Session
from app.models import models
import random

class PrioritizationService:
    def __init__(self, db: Session):
        self.db = db

    def score_finding(self, finding_id: int):
        """Calculates exploitability and impact scores for a finding."""
        finding = self.db.query(models.Finding).filter(models.Finding.id == finding_id).first()
        if not finding:
            return None

        # Heuristic scoring
        exploitability = 0.5
        impact = 0.5

        if finding.severity == "critical":
            impact = 0.9
            exploitability = 0.7
        elif finding.severity == "high":
            impact = 0.7
            exploitability = 0.5

        # Adjust based on binary protections
        binary = finding.function.binary
        if binary.protections:
            prots = binary.protections
            if prots.get("ASLR"): exploitability -= 0.1
            if prots.get("NX"): exploitability -= 0.1
            if prots.get("Canary"): exploitability -= 0.1

        composite = (exploitability * 0.4) + (impact * 0.6)

        priority = "medium"
        if composite > 0.8: priority = "critical"
        elif composite > 0.6: priority = "high"
        elif composite < 0.3: priority = "low"

        score = models.FindingScore(
            finding_id=finding_id,
            exploitability=max(0.1, exploitability),
            impact=impact,
            composite_score=composite,
            priority=priority,
            notes=f"Auto-calculated priority based on {finding.severity} severity and binary protections."
        )
        self.db.add(score)
        self.db.commit()
        return score

    def map_attack_paths(self, project_id: int):
        """Simulates mapping potential attack paths from findings."""
        findings = self.db.query(models.Finding).join(models.Function).join(models.Binary).join(models.Device).filter(
            models.Device.project_id == project_id
        ).all()

        paths = []
        # Logical grouping: Remote bug -> Local priv esc -> Lateral move
        for f in findings:
            if f.function.is_zero_click_candidate:
                paths.append({
                    "name": f"Zero-Click Entry via {f.function.name}",
                    "steps": ["Initial Access", "Persistence"],
                    "start_node": f.id
                })

        return paths
