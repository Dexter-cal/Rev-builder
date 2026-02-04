from sqlalchemy.orm import Session
from app.models.models import HardwareJob, HardwareInterface, FirmwareImage, Device, PayloadSuccessRate, Payload
import json
import datetime
import random

class HardwareAttackService:
    def __init__(self, db: Session):
        self.db = db

    def discover_interfaces(self, device_id: int):
        """Simulates discovering hardware interfaces like UART, JTAG, SPI."""
        # In a real tool, this might interface with a Bus Pirate or JTAGulator
        interfaces = [
            {"type": "UART", "pins": {"TX": 1, "RX": 2, "GND": 3}, "voltage": 3.3, "baud_rate": 115200},
            {"type": "SPI", "pins": {"MOSI": 4, "MISO": 5, "CLK": 6, "CS": 7}, "voltage": 3.3},
            {"type": "JTAG", "pins": {"TDI": 8, "TDO": 9, "TCK": 10, "TMS": 11, "TRST": 12}, "voltage": 3.3}
        ]

        results = []
        for iface in interfaces:
            new_iface = HardwareInterface(
                device_id=device_id,
                type=iface["type"],
                pins=iface["pins"],
                voltage=iface["voltage"],
                baud_rate=iface.get("baud_rate"),
                notes=f"Auto-discovered {iface['type']} interface."
            )
            self.db.add(new_iface)
            results.append(new_iface)

        self.db.commit()
        return results

    def run_hardware_action(self, device_id: int, interface_type: str, action: str):
        """Executes an action on a specific hardware interface."""
        job = HardwareJob(
            device_id=device_id,
            interface=interface_type,
            action=action,
            status="running",
            data_captured={}
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        # Simulation of hardware interaction
        if action == "sniff":
            job.data_captured = {"log": "Captured bootloader logs: U-Boot 2022.04...", "entropy": 0.82}
        elif action == "dump":
            job.data_captured = {"file_path": f"/storage/firmware/dump_{device_id}_{interface_type.lower()}.bin", "size": 16777216}
        elif action == "fuzz":
            job.data_captured = {"crashes": [{"offset": "0x400", "type": "overflow"}]}

        job.status = "completed"
        self.db.commit()
        return job

    def get_next_steps(self, device_id: int):
        """Suggests next steps based on connected hardware interfaces."""
        interfaces = self.db.query(HardwareInterface).filter(HardwareInterface.device_id == device_id).all()
        suggestions = []

        for iface in interfaces:
            if iface.type == "UART":
                suggestions.append({
                    "title": "UART Console Access",
                    "description": "Try to interrupt the bootloader (U-Boot) to get a root shell.",
                    "priority": "high",
                    "action": "open_terminal"
                })
            elif iface.type == "JTAG":
                suggestions.append({
                    "title": "JTAG Memory Dump",
                    "description": "Full CPU access detected. Dump RAM to find encryption keys or sensitive strings.",
                    "priority": "critical",
                    "action": "dump_memory"
                })
            elif iface.type == "SPI":
                suggestions.append({
                    "title": "Flash Extraction",
                    "description": "SPI Flash detected. Dump the firmware image for binary analysis.",
                    "priority": "medium",
                    "action": "dump_flash"
                })

        return suggestions

    def track_payload_success(self, payload_id: int, result: str, arch: str, os: str):
        """Tracks the success rate of hardware-level payloads."""
        rate = self.db.query(PayloadSuccessRate).filter(
            PayloadSuccessRate.payload_id == payload_id,
            PayloadSuccessRate.arch == arch,
            PayloadSuccessRate.os == os
        ).first()

        if not rate:
            rate = PayloadSuccessRate(payload_id=payload_id, arch=arch, os=os)
            self.db.add(rate)

        if result == "success":
            rate.success_count += 1
        elif result == "fail":
            rate.fail_count += 1
        elif result == "crash":
            rate.crash_count += 1

        self.db.commit()
        return rate

    def get_recommended_payloads(self, arch: str, os: str):
        """Recommends payloads based on historical success rates for the given architecture and OS."""
        rates = self.db.query(PayloadSuccessRate).filter(
            PayloadSuccessRate.arch == arch,
            PayloadSuccessRate.os == os
        ).order_by(PayloadSuccessRate.success_count.desc()).all()

        recommendations = []
        for r in rates:
            payload = self.db.query(Payload).filter(Payload.id == r.payload_id).first()
            if payload:
                success_pct = (r.success_count / (r.success_count + r.fail_count + r.crash_count + 1)) * 100
                recommendations.append({
                    "id": payload.id,
                    "name": payload.name,
                    "success_rate": f"{success_pct:.1f}%",
                    "notes": r.notes
                })

        return recommendations
