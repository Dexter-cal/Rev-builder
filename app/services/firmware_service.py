from sqlalchemy.orm import Session
from app.models.models import FirmwareImage, FirmwareAnalysis, RecompilationJob, Binary
import os
import shutil
import subprocess
import datetime
import hashlib

class FirmwareService:
    def __init__(self, db: Session):
        self.db = db

    def register_firmware(self, device_id: int, file_path: str, version: str = "1.0.0"):
        """Registers a dumped firmware image in the database."""
        if not os.path.exists(file_path):
            # For simulation, we'll create a dummy file if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(os.urandom(1024 * 1024)) # 1MB dummy firmware

        with open(file_path, "rb") as f:
            file_data = f.read()
            file_hash = hashlib.sha256(file_data).hexdigest()
            size = len(file_data)

        firmware = FirmwareImage(
            device_id=device_id,
            version=version,
            file_path=file_path,
            hash=file_hash,
            size=size,
            notes=f"Firmware dump registered at {datetime.datetime.now()}"
        )
        self.db.add(firmware)
        self.db.commit()
        self.db.refresh(firmware)
        return firmware

    def extract_firmware(self, firmware_id: int):
        """Simulates firmware extraction using binwalk."""
        firmware = self.db.query(FirmwareImage).filter(FirmwareImage.id == firmware_id).first()
        if not firmware:
            return None

        extraction_path = firmware.file_path + "_extracted"
        os.makedirs(extraction_path, exist_ok=True)

        # Simulate extracted files
        dummy_files = ["etc/passwd", "etc/shadow", "bin/busybox", "bin/httpd", "usr/lib/libssl.so"]
        for df in dummy_files:
            full_path = os.path.join(extraction_path, df)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(f"Dummy content for {df}")

        firmware.extraction_path = extraction_path
        self.db.commit()
        return extraction_path

    def run_analysis(self, firmware_id: int, tool: str):
        """Simulates running firmware analysis tools like emba or firmwalker."""
        firmware = self.db.query(FirmwareImage).filter(FirmwareImage.id == firmware_id).first()
        if not firmware:
            return None

        results = {}
        if tool == "binwalk":
            results = {
                "scan_results": [
                    {"decimal": 0, "hex": "0x0", "description": "TRX firmware header, length 16777216 bytes"},
                    {"decimal": 28, "hex": "0x1C", "description": "LZMA compressed data, dictionary size: 65536 bytes, uncompressed size: 543210 bytes"},
                    {"decimal": 12345, "hex": "0x3039", "description": "Squashfs filesystem, little endian, version 4.0, compression:xz, size: 8765432 bytes"}
                ]
            }
        elif tool == "firmwalker":
            results = {
                "interesting_files": [
                    {"file": "etc/passwd", "reason": "Contains user accounts"},
                    {"file": "etc/shadow", "reason": "Contains password hashes"},
                    {"file": "etc/ssl/certs", "reason": "Encryption assets"}
                ],
                "strings": ["root", "admin", "password", "telnet", "ssh"]
            }
        elif tool == "emba":
            results = {
                "vulnerabilities": [
                    {"severity": "high", "description": "Outdated busybox version", "cve": "CVE-2022-28391"},
                    {"severity": "critical", "description": "Insecure default root password", "recommendation": "Change default password"}
                ],
                "protections": {"aslr": "disabled", "nx": "enabled"}
            }

        analysis = FirmwareAnalysis(
            firmware_id=firmware_id,
            tool_name=tool,
            results=results
        )
        self.db.add(analysis)
        self.db.commit()
        return analysis

    def create_recompilation_job(self, project_id: int, binary_id: int, source_code: str, target_arch: str):
        """Creates a job to recompile or patch a binary."""
        job = RecompilationJob(
            project_id=project_id,
            binary_id=binary_id,
            source_code=source_code,
            target_arch=target_arch,
            status="pending",
            logs="Job created."
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def run_recompilation(self, job_id: int):
        """Executes the recompilation job."""
        job = self.db.query(RecompilationJob).filter(RecompilationJob.id == job_id).first()
        if not job:
            return None

        job.status = "compiling"
        job.logs += "\nStarting compilation..."
        self.db.commit()

        # Simulate compilation
        try:
            # In a real tool, we might use cross-compilers like arm-linux-gnueabi-gcc
            job.logs += f"\nInvoking compiler for {job.target_arch}..."
            # For simulation, we'll just wait a bit and pretend it worked
            output_path = f"/storage/binaries/patched_{job_id}.bin"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(b"\x7fELF\x01\x01\x01\x00" + b"\x00" * 64) # Dummy ELF header

            # Register output binary
            new_bin = Binary(
                device_id=None, # Not yet assigned to a device
                path=output_path,
                hash=hashlib.sha256(b"dummy").hexdigest(),
                arch=job.target_arch,
                file_type="ELF",
                size=72,
                notes=f"Recompiled from Job #{job_id}"
            )
            self.db.add(new_bin)
            self.db.commit()
            self.db.refresh(new_bin)

            job.output_binary_id = new_bin.id
            job.status = "success"
            job.logs += "\nCompilation successful. Artifact saved."
        except Exception as e:
            job.status = "failed"
            job.logs += f"\nError: {str(e)}"

        self.db.commit()
        return job
