import random
import time
from sqlalchemy.orm import Session
from app.models import models

class FuzzingService:
    def __init__(self, db: Session):
        self.db = db

    def start_fuzzing(self, binary_id: int, config: dict, target_function_id: int = None):
        job = models.FuzzingJob(
            binary_id=binary_id,
            target_function_id=target_function_id,
            status="running",
            config=config
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def run_simulation(self, job_id: int):
        job = self.db.query(models.FuzzingJob).filter(models.FuzzingJob.id == job_id).first()
        if not job:
            return None

        # Simulate fuzzing process
        # In a real app, this would spawn a process like AFL++ or libFuzzer

        crashes_found = random.randint(0, 3)
        for _ in range(crashes_found):
            result = models.FuzzingResult(
                job_id=job.id,
                input_data=f"fuzz_input_{random.getrandbits(32):x}",
                crash_log="SIGSEGV at 0x401215",
                stack_trace="[#0] 0x401215 in vulnerable_func ()\n[#1] 0x401250 in main ()",
                severity="high"
            )
            self.db.add(result)

            # If we find a crash, also create a Finding
            finding = models.Finding(
                function_id=job.target_function_id,
                severity="high",
                confidence=0.9,
                evidence=result.crash_log,
                recommendation="Fix memory corruption by implementing bounds checks.",
                risk_score=85
            )
            self.db.add(finding)

        job.status = "completed"
        self.db.commit()

        # Log to project-specific logs as well
        # In a real tool, we might save the crash inputs as assets

        return crashes_found
