import subprocess
import os
from sqlalchemy.orm import Session
from app.models import models
from app.services.asset_service import AssetService

class CompilerService:
    @staticmethod
    def compile_c(db: Session, project_id: int, source_code: str, output_name: str):
        # Save source to asset storage
        source_filename = f"{output_name}.c"
        source_path = AssetService.save_asset(project_id, "source", source_filename, source_code.encode())

        # Determine output path
        output_filename = output_name
        output_path = AssetService.get_asset_path(project_id, "binaries", output_filename)

        # Run GCC
        try:
            result = subprocess.run(
                ["gcc", source_path, "-o", output_path],
                capture_output=True,
                text=True,
                check=True
            )

            # Register the new binary in the database
            # We need a device, for now we associate it with the project's first device or a generic one
            device = db.query(models.Device).filter(models.Device.project_id == project_id).first()
            if not device:
                device = models.Device(project_id=project_id, name="Local Build Env", type="virtual")
                db.add(device)
                db.commit()
                db.refresh(device)

            binary = models.Binary(
                device_id=device.id,
                path=output_path,
                hash="locally_compiled",
                arch="x86_64",
                file_type="ELF (Compiled)",
                size=os.path.getsize(output_path)
            )
            db.add(binary)
            db.commit()

            return {"success": True, "binary_id": binary.id, "logs": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"success": False, "logs": e.stderr}

class WeaponizerService:
    @staticmethod
    def generate_real_exploit(db: Session, finding_id: int, project_id: int):
        finding = db.query(models.Finding).filter(models.Finding.id == finding_id).first()
        if not finding:
            return None

        # Use pwntools-style template
        template = f"""# Weaponized Exploit for Finding #{finding.id}
# Vulnerability: {finding.severity} {finding.risk_score}
# Recommendation: {finding.recommendation}

from pwn import *

context.arch = 'amd64'
context.os = 'linux'

# Replace with target details
target_ip = '127.0.0.1'
target_port = 1337

def exploit():
    # r = remote(target_ip, target_port)
    # r = process('./vulnerable_binary')

    # Example Buffer Overflow payload
    payload = b'A' * 128
    payload += p64(0x401234) # Simulated return address

    # log.info("Sending payload...")
    # r.sendline(payload)
    # r.interactive()
    print("[+] Exploit script generated successfully")

if __name__ == '__main__':
    exploit()
"""
        weapon = models.ExploitWeapon(
            project_id=project_id,
            name=f"Exploit_Finding_{finding_id}",
            code=template,
            language="python",
            target_arch="x86_64"
        )
        db.add(weapon)
        db.commit()
        db.refresh(weapon)
        return weapon
