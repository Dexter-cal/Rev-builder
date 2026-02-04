from sqlalchemy.orm import Session
from app.models import models
from typing import List, Optional
import random

class WordlistService:
    def __init__(self, db: Session):
        self.db = db

    def create_wordlist(self, name: str, content: str, category: str, project_id: Optional[int] = None, is_ai: bool = False):
        wordlist = models.Wordlist(
            name=name,
            content=content,
            category=category,
            project_id=project_id,
            is_ai_generated=is_ai
        )
        self.db.add(wordlist)
        self.db.commit()
        self.db.refresh(wordlist)
        return wordlist

    def get_wordlists(self, project_id: Optional[int] = None, category: Optional[str] = None):
        query = self.db.query(models.Wordlist)
        if project_id:
            query = query.filter(models.Wordlist.project_id == project_id)
        if category:
            query = query.filter(models.Wordlist.category == category)
        return query.all()

    def generate_ai_wordlist(self, project_id: int, category: str, context: str):
        """
        Simulates AI-driven wordlist generation.
        In a real scenario, this would call an LLM with the context (e.g., target company name,
        technologies found, employee names from recon).
        """
        # Simulated AI output based on context
        ai_words = []
        if category == "passwords":
            base_words = [context.lower(), "admin", "password", "security", "winter", "summer"]
            for w in base_words:
                ai_words.extend([f"{w}123", f"{w}!", f"{w}2024", f"{w}2023"])
        elif category == "usernames":
            ai_words = ["admin", "root", "support", f"user_{context.lower()}", "it_admin"]
        elif category == "subdomains":
            ai_words = ["dev", "staging", "api", "vpn", "mail", "internal", "test"]

        random.shuffle(ai_words)
        content = "\n".join(ai_words)

        name = f"AI Generated {category.capitalize()} - {context}"
        return self.create_wordlist(name, content, category, project_id, is_ai=True)

    def generate_contextual_bruteforce(self, device_id: int):
        device = self.db.query(models.Device).filter(models.Device.id == device_id).first()
        if not device:
            return None

        context = f"{device.name} {device.os} {device.type}"
        return self.generate_ai_wordlist(device.project_id, "passwords", context)
