from app.database.session import SessionLocal
from app.models import models
from app.database.base import Base
from app.database.session import engine
import json

def setup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Project and Device
    project = db.query(models.Project).filter(models.Project.id == 1).first()
    if not project:
        project = models.Project(id=1, name="Eagle Eye", status="active")
        db.add(project)
        db.commit()

    device = db.query(models.Device).filter(models.Device.id == 1).first()
    if not device:
        device = models.Device(id=1, project_id=1, name="Router-Main", ip="192.168.1.1")
        db.add(device)
        db.commit()

    # Exploit Modules
    m1 = models.ExploitModule(
        name="linux/http/apache_struts_rce",
        description="Apache Struts Jakata Multipart Parser RCE",
        author="unknown",
        platform="linux",
        arch=["x86", "x64"],
        options={
            "RHOST": {"required": True, "desc": "Target address"},
            "RPORT": {"required": True, "desc": "Target port", "default": "8080"}
        },
        payload_type="reverse_tcp"
    )

    m2 = models.ExploitModule(
        name="multi/samba/usermap_script",
        description="Samba username map script Command Execution",
        author="jules",
        platform="multi",
        arch=["x86", "arm"],
        options={
            "RHOST": {"required": True, "desc": "Target address"},
            "RPORT": {"required": True, "desc": "Target port", "default": "139"}
        },
        payload_type="cmd"
    )

    for m in [m1, m2]:
        existing = db.query(models.ExploitModule).filter(models.ExploitModule.name == m.name).first()
        if not existing:
            db.add(m)

    db.commit()

    # Vulnerability Mapping
    v1 = models.VulnerabilityMap(
        software_name="Apache Struts",
        version_range="2.3.5 - 2.3.31",
        cve_id="CVE-2017-5638",
        description="Remote Code Execution via Jakata Multipart Parser",
        exploit_module_id=1 # Maps to m1
    )

    db.add(v1)

    # AI Models
    ai1 = models.AIModel(
        name="Gemini-1.5-Pro",
        model_type="LLM",
        api_key="sk-...",
        base_url="https://generativelanguage.googleapis.com",
        profile_config={"temperature": 0.7, "top_p": 0.9},
        enabled=True
    )
    ai2 = models.AIModel(
        name="GPT-4o",
        model_type="LLM",
        api_key="sk-...",
        base_url="https://api.openai.com/v1",
        profile_config={"temperature": 0.5},
        enabled=False
    )

    for ai in [ai1, ai2]:
        existing = db.query(models.AIModel).filter(models.AIModel.name == ai.name).first()
        if not existing:
            db.add(ai)

    db.commit()
    db.close()

if __name__ == "__main__":
    setup()
    print("Seeded advanced exploit data.")
