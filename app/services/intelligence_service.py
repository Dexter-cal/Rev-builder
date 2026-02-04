from sqlalchemy.orm import Session
from app.models import models
from typing import List, Dict
from app.services.zero_click_service import ZeroClickService

class IntelligenceService:
    def __init__(self, db: Session):
        self.db = db
        self.zero_click_service = ZeroClickService(db)

    def get_suggestions(self, finding_id: int) -> List[Dict]:
        finding = self.db.query(models.Finding).filter(models.Finding.id == finding_id).first()
        if not finding:
            return []

        func = finding.function
        binary = func.binary
        protections = binary.protections or {}
        vuln_type = func.vuln_type

        suggestions = []

        # 1. Base vulnerability suggestions
        if vuln_type == "buffer_overflow":
            if protections.get("NX"):
                suggestions.append({
                    "title": "Bypass NX with ROP",
                    "description": "Non-Executable stack detected. You should use a Return Oriented Programming (ROP) chain to execute system commands or make stack executable.",
                    "priority": "high",
                    "action_type": "generate_rop"
                })
            else:
                suggestions.append({
                    "title": "Direct Shellcode Injection",
                    "description": "Stack is executable. You can inject shellcode directly and jump to it.",
                    "priority": "high",
                    "action_type": "generate_shellcode"
                })

            if protections.get("ASLR") or protections.get("PIE"):
                suggestions.append({
                    "title": "Need Address Leak",
                    "description": "ASLR/PIE is enabled. Cross-reference with a format string or heap leak finding to find base addresses.",
                    "priority": "critical",
                    "action_type": "search_leaks"
                })

        elif vuln_type == "format_string":
            suggestions.append({
                "title": "Information Leak",
                "description": "Use this format string vulnerability to leak the Canary, LIBC base, or Stack addresses.",
                "priority": "high",
                "action_type": "leak_addresses"
            })
            suggestions.append({
                "title": "Arbitrary Write",
                "description": "Use %n to overwrite the Global Offset Table (GOT) or return addresses.",
                "priority": "medium",
                "action_type": "got_overwrite"
            })

        # 2. Cross-referencing logic
        all_findings = self.db.query(models.Finding).join(models.Function).filter(models.Function.binary_id == binary.id).all()

        has_leak = any(f.function.vuln_type in ["format_string", "info_disclosure"] for f in all_findings)
        has_overflow = any(f.function.vuln_type == "buffer_overflow" for f in all_findings)

        if has_leak and has_overflow and vuln_type == "buffer_overflow":
            suggestions.append({
                "title": "Full RCE Chain Possible",
                "description": "Combining your existing address leak with this overflow allows for a full ASLR/NX bypass chain.",
                "priority": "critical",
                "action_type": "build_chain"
            })

        # 3. Zero-click suggestions
        if func.is_zero_click_candidate:
            zc_suggestions = self.zero_click_service.get_zero_click_suggestions(func)
            suggestions.extend(zc_suggestions)

        return suggestions

    def build_exploit_chain(self, finding_ids: List[int], name: str) -> models.ExploitChain:
        findings = self.db.query(models.Finding).filter(models.Finding.id.in_(finding_ids)).all()
        if not findings: return None

        steps = []
        for i, f in enumerate(findings):
            steps.append({
                "step": i + 1,
                "finding_id": f.id,
                "action": f"Exploit {f.function.vuln_type} in {f.function.name}",
                "description": f.recommendation
            })

        # Generate combined code (Simulated AI generation)
        combined_code = f"# Combined Exploit Chain: {name}\n"
        combined_code += "from pwn import *\n\n"
        for i, f in enumerate(findings):
            combined_code += f"# Step {i+1}: {f.function.vuln_type} at {f.function.offset}\n"
            combined_code += f"def exploit_step_{i+1}():\n    pass\n\n"

        chain = models.ExploitChain(
            name=name,
            steps=steps,
            target_device_id=findings[0].function.binary.device_id,
            target_function_id=findings[0].function_id,
            notes=combined_code,
            result="Ready"
        )
        self.db.add(chain)
        self.db.commit()
        self.db.refresh(chain)
        return chain

    def analyze_binary_protections(self, binary_id: int):
        # Simulated checksec
        binary = self.db.query(models.Binary).filter(models.Binary.id == binary_id).first()
        if not binary: return

        # In a real tool, we'd run 'checksec' or similar
        binary.protections = {
            "NX": True,
            "ASLR": True,
            "Canary": random.choice([True, False]),
            "PIE": random.choice([True, False]),
            "RELRO": "Full"
        }
        self.db.commit()
        return binary.protections
import random
