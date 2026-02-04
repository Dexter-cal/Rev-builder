from sqlalchemy.orm import Session
from app.models import models
from typing import List, Dict
import re

class ZeroClickService:
    def __init__(self, db: Session):
        self.db = db

        self.zero_click_keywords = {
            "messaging": [r"message", r"sms", r"mms", r"whatsapp", r"signal", r"imessage", r"chat", r"rcs"],
            "notification": [r"notify", r"push", r"banner", r"alert", r"render_preview"],
            "background_service": [r"sync", r"daemon", r"fetch", r"poll", r"heartbeat", r"background"],
            "media_parser": [r"parse", r"decode", r"render", r"image", r"video", r"audio", r"jpeg", r"png", r"mp4", r"codec"],
            "voip": [r"sip", r"rtp", r"webrtc", r"call", r"signaling", r"sdp"]
        }

    def discover_candidates(self, binary_id: int) -> List[models.Function]:
        """Scans functions in a binary for potential zero-click entry points."""
        binary = self.db.query(models.Binary).filter(models.Binary.id == binary_id).first()
        if not binary:
            return []

        candidates = []
        for func in binary.functions:
            # Simple keyword matching for demo/MVP
            matched_surface = None
            for surface, keywords in self.zero_click_keywords.items():
                for kw in keywords:
                    if re.search(kw, func.name, re.IGNORECASE):
                        matched_surface = surface
                        break
                if matched_surface:
                    break

            if matched_surface:
                func.is_zero_click_candidate = True
                func.surface_type = matched_surface
                candidates.append(func)

        self.db.commit()
        return candidates

    def get_zero_click_suggestions(self, func: models.Function) -> List[Dict]:
        """Provides specific suggestions for zero-click research on a function."""
        if not func.is_zero_click_candidate:
            return []

        suggestions = []
        surface = func.surface_type

        if surface == "media_parser":
            suggestions.append({
                "title": "Malformed Media Fuzzing",
                "description": f"This function appears to parse media data. Suggest using a fuzzer with a corpus of malformed {func.name.split('_')[-1] if '_' in func.name else 'media'} files.",
                "priority": "high",
                "action_type": "fuzz_media"
            })
        elif surface == "messaging":
            suggestions.append({
                "title": "Zero-Click Message Injection",
                "description": "This function handles incoming messages. Test with malformed protocol buffers or XML payloads that trigger automatically on receipt.",
                "priority": "critical",
                "action_type": "inject_message"
            })
        elif surface == "notification":
            suggestions.append({
                "title": "Notification Preview Exploit",
                "description": "Code handles notification rendering. A bug here could trigger RCE as soon as the notification appears on the lock screen.",
                "priority": "critical",
                "action_type": "fuzz_notification"
            })

        return suggestions

    def generate_zero_click_payload_template(self, surface_type: str) -> str:
        templates = {
            "messaging": """
# Zero-Click Messaging Exploit Template
import socket

def craft_malformed_msg():
    # Example: Malformed length field to trigger overflow
    payload = b"\\x00\\x00\\xff\\xff" # Oversized length
    payload += b"A" * 1024 # Junk
    return payload

def send_to_target(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    s.send(craft_malformed_msg())
    s.close()
""",
            "media_parser": """
# Zero-Click Media Exploit Template (JPEG/MPEG)
def generate_malformed_header():
    # Example: Crafting a chunk with invalid dimensions
    header = b"\\xff\\xd8" # SOI
    header += b"\\xff\\xc0" # SOF0
    header += b"\\x00\\x02" # Length
    header += b"\\x00\\x00" # Height 0
    header += b"\\x00\\x00" # Width 0
    return header
"""
        }
        return templates.get(surface_type, "# No specific template for this surface.")
