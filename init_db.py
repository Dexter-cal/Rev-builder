from app.database.base import Base
from app.database.session import engine, SessionLocal
from app.models.models import ExternalSource
from app.models import models

def seed_data(db):
    sources = [
        {
            "name": "Exploit-DB",
            "url": "https://www.exploit-db.com",
            "description": "A huge public archive of public exploits and PoC code (remote, local, DoS, shellcode, web apps, etc.).",
            "type": "exploit_db"
        },
        {
            "name": "Rapid7 Vulnerability & Exploit Database",
            "url": "https://www.rapid7.com/db/",
            "description": "A commercial-grade vulnerability and exploit database with verified exploits and remediation guidance.",
            "type": "exploit_db"
        },
        {
            "name": "CXSecurity",
            "url": "https://cxsecurity.com/",
            "description": "A public exploit database with filters for local/remote, risk level, and author.",
            "type": "exploit_db"
        },
        {
            "name": "Metasploit Framework",
            "url": "https://github.com/rapid7/metasploit-framework",
            "description": "Metasploit's built-in collection of modules (exploits, payloads, auxiliaries).",
            "type": "exploit_framework"
        },
        {
            "name": "NIST National Vulnerability Database (NVD)",
            "url": "https://nvd.nist.gov",
            "description": "The official US government CVE-centric vulnerability database.",
            "type": "cve_db"
        },
        {
            "name": "MITRE CVE List",
            "url": "https://cve.mitre.org",
            "description": "The canonical list of CVE IDs and brief descriptions.",
            "type": "cve_db"
        },
        {
            "name": "GitHub Exploit Repos",
            "url": "https://github.com/offensive-security/exploitdb",
            "description": "Various GitHub repositories containing PoC exploits and security research.",
            "type": "poc_repo"
        }
    ]

    for source_data in sources:
        # Check if source already exists
        source = db.query(ExternalSource).filter(ExternalSource.name == source_data["name"]).first()
        if not source:
            source = ExternalSource(**source_data)
            db.add(source)

    db.commit()
    print("Seeded external sources.")

def seed_patterns(db):
    patterns = [
        {
            "name": "Unsafe gets() usage",
            "language": "asm",
            "pattern": "call gets",
            "description": "The gets() function does not check for buffer length and is highly vulnerable to stack-based buffer overflows.",
            "severity": "critical",
            "confidence_base": 0.9,
            "arch": ["x86", "x86_64", "arm"],
            "tags": ["buffer_overflow", "rce"]
        },
        {
            "name": "Unsafe scanf() with %s",
            "language": "asm",
            "pattern": "call scanf",
            "description": "Using scanf with %s without width limits can lead to buffer overflows.",
            "severity": "high",
            "confidence_base": 0.7,
            "arch": ["x86", "x86_64"],
            "tags": ["buffer_overflow"]
        }
    ]

    for pattern_data in patterns:
        pattern = db.query(models.Pattern).filter(models.Pattern.name == pattern_data["name"]).first()
        if not pattern:
            pattern = models.Pattern(**pattern_data)
            db.add(pattern)

    db.commit()
    print("Seeded vulnerability patterns.")

def seed_templates_and_tags(db):
    # Seed Project Templates
    templates = [
        {"name": "Router Audit", "description": "Focused on firmware analysis and network services of embedded routers."},
        {"name": "IoT Camera Lab", "description": "Security evaluation of IP cameras, including ONVIF and web interfaces."},
        {"name": "Server Hardening", "description": "Audit of Linux/Windows server configurations and exposed binaries."}
    ]
    for t_data in templates:
        if not db.query(models.ProjectTemplate).filter(models.ProjectTemplate.name == t_data["name"]).first():
            db.add(models.ProjectTemplate(**t_data))

    # Seed Tags
    tags = [
        {"name": "critical", "color": "#ef4444"},
        {"name": "lab-only", "color": "#3b82f6"},
        {"name": "needs-review", "color": "#f59e0b"},
        {"name": "dangerous", "color": "#7c3aed"}
    ]
    for tag_data in tags:
        if not db.query(models.Tag).filter(models.Tag.name == tag_data["name"]).first():
            db.add(models.Tag(**tag_data))

    db.commit()
    print("Seeded project templates and tags.")

def init_db():
    print("Initializing the database...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_data(db)
        seed_patterns(db)
        seed_templates_and_tags(db)
    finally:
        db.close()

    print("Database initialized and seeded successfully.")

if __name__ == "__main__":
    init_db()
