from sqlalchemy.orm import Session
from app.models import models

class PlaybookService:
    def __init__(self, db: Session):
        self.db = db

    def get_playbooks(self, category: str = None):
        query = self.db.query(models.Playbook)
        if category:
            query = query.filter(models.Playbook.category == category)

        playbooks = query.all()
        if not playbooks:
            self.seed_defaults()
            playbooks = query.all()
        return playbooks

    def seed_defaults(self):
        defaults = [
            {
                "name": "Standard Firmware Audit",
                "description": "Extract filesystem, check for default credentials, and scan binaries for overflows.",
                "category": "Firmware",
                "workflow_data": {"steps": ["Extract", "Firmwalker", "Symbol Analysis"]}
            },
            {
                "name": "JTAG Hardware Attack",
                "description": "Full CPU access workflow for reading memory and bypassing boot security.",
                "category": "Hardware",
                "workflow_data": {"steps": ["Connect", "Dump RAM", "Find Keys"]}
            },
            {
                "name": "Zero-Click Discovery",
                "description": "Advanced heuristics for finding interaction-less entry points in messaging apps.",
                "category": "Mobile",
                "workflow_data": {"steps": ["Heuristics", "Media Parser Fuzzing"]}
            }
        ]
        for d in defaults:
            if not self.db.query(models.Playbook).filter(models.Playbook.name == d["name"]).first():
                p = models.Playbook(**d)
                self.db.add(p)
        self.db.commit()

    def generate_threat_model(self, project_id: int):
        """Simulates auto-generating a threat model for the project assets."""
        # Simple simulation
        assets = ["Web Interface", "UART Debug Port", "SSH Service"]
        threats = ["Remote Exploit", "Physical Tampering", "Credential Stuffing"]

        model = models.ThreatModel(
            project_id=project_id,
            graph_data={"assets": assets, "threats": threats},
            risk_summary="High risk due to exposed UART and outdated busybox."
        )
        self.db.add(model)
        self.db.commit()
        return model
