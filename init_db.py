from app.database.base import Base
from app.database.session import engine, SessionLocal
from app.models.models import ExternalSource
import app.models

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

def init_db():
    print("Initializing the database...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()

    print("Database initialized and seeded successfully.")

if __name__ == "__main__":
    init_db()
