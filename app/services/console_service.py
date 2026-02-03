from sqlalchemy.orm import Session
from app.models import models
import json

class ConsoleService:
    def __init__(self, db: Session):
        self.db = db
        self.active_module = None
        self.options = {}

    def execute_command(self, command_str: str):
        parts = command_str.strip().split()
        if not parts:
            return ""

        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "help":
            return "Available commands: help, use, set, show options, show modules, run, exit"

        if cmd == "show" and args:
            sub = args[0].lower()
            if sub == "modules":
                modules = self.db.query(models.ExploitModule).all()
                out = "Exploit Modules\n===============\n\n"
                out += "Name\tDescription\n----\t-----------\n"
                for m in modules:
                    out += f"{m.name}\t{m.description[:40]}...\n"
                return out
            if sub == "options":
                if not self.active_module:
                    return "No module selected."
                out = f"Options for {self.active_module.name}\n==============================\n\n"
                out += "Name\tCurrent Setting\tRequired\tDescription\n----\t---------------\t--------\t-----------\n"
                for name, opt in self.active_module.options.items():
                    val = self.options.get(name, "")
                    req = "yes" if opt.get("required") else "no"
                    desc = opt.get("desc", "")
                    out += f"{name}\t{val}\t{req}\t{desc}\n"
                return out

        if cmd == "use" and args:
            module_name = args[0]
            module = self.db.query(models.ExploitModule).filter(models.ExploitModule.name == module_name).first()
            if module:
                self.active_module = module
                self.options = {} # Reset options
                return f"Using module: {module.name}"
            return "Module not found."

        if cmd == "set" and len(args) >= 2:
            name = args[0].upper()
            value = " ".join(args[1:])
            if self.active_module and name in self.active_module.options:
                self.options[name] = value
                return f"{name} => {value}"
            return f"Invalid option: {name}"

        if cmd == "run":
            if not self.active_module:
                return "No module selected."

            # Check required options
            for name, opt in self.active_module.options.items():
                if opt.get("required") and name not in self.options:
                    return f"Missing required option: {name}"

            # Simulate execution
            output = f"[*] Started exploit {self.active_module.name}...\n"
            output += f"[*] Target: {self.options.get('RHOST', 'Unknown')}\n"
            output += "[+] Sending payload...\n"
            output += "[*] Exploit successful! Shell established.\n"
            return output

        return f"Unknown command: {cmd}"
