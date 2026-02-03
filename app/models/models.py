from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Float, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

# Association tables for many-to-many relationships
finding_references = Table(
    "finding_references",
    Base.metadata,
    Column("finding_id", Integer, ForeignKey("findings.id"), primary_key=True),
    Column("reference_id", Integer, ForeignKey("vulnerability_references.id"), primary_key=True),
)

pattern_references = Table(
    "pattern_references",
    Base.metadata,
    Column("pattern_id", Integer, ForeignKey("patterns.id"), primary_key=True),
    Column("reference_id", Integer, ForeignKey("vulnerability_references.id"), primary_key=True),
)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String)  # planning, active, completed
    authorized_targets = Column(JSON)  # Array of IPs/domains/devices
    notes = Column(Text)

    devices = relationship("Device", back_populates="project")
    reports = relationship("Report", back_populates="project")

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    type = Column(String)  # phone, router, IoT, server, embedded
    os = Column(String)
    firmware_version = Column(String)
    ip = Column(String)
    mac = Column(String)
    serial = Column(String)
    last_seen = Column(DateTime)
    notes = Column(Text)

    project = relationship("Project", back_populates="devices")
    binaries = relationship("Binary", back_populates="device")
    sessions = relationship("Session", back_populates="device")
    payloads = relationship("Payload", back_populates="target_device")
    exploit_chains = relationship("ExploitChain", back_populates="target_device")

class Binary(Base):
    __tablename__ = "binaries"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    path = Column(String)
    hash = Column(String)  # SHA-256
    arch = Column(String)  # x86, ARM, etc.
    file_type = Column(String)  # ELF, PE, Mach-O, DEX, firmware
    size = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    notes = Column(Text)

    device = relationship("Device", back_populates="binaries")
    functions = relationship("Function", back_populates="binary")

class Function(Base):
    __tablename__ = "functions"

    id = Column(Integer, primary_key=True, index=True)
    binary_id = Column(Integer, ForeignKey("binaries.id"))
    name = Column(String)
    offset = Column(String)
    size = Column(Integer)
    danger_score = Column(Integer)  # 0-100
    vuln_type = Column(String)
    assembly_snippet = Column(Text)
    python_like = Column(Text)
    notes = Column(Text)

    binary = relationship("Binary", back_populates="functions")
    findings = relationship("Finding", back_populates="function")
    payloads = relationship("Payload", back_populates="target_function")
    exploit_chains = relationship("ExploitChain", back_populates="target_function")
    ai_analyses = relationship("AIAnalysis", back_populates="function")

class Pattern(Base):
    __tablename__ = "patterns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    language = Column(String)
    pattern = Column(Text)
    description = Column(Text)
    severity = Column(String)  # critical, high, medium, low
    confidence_base = Column(Float)  # 0-1
    arch = Column(JSON)  # Array: ["x86", "arm"]
    tags = Column(JSON)  # Array: ["buffer_overflow", "rce"]
    created_at = Column(DateTime, server_default=func.now())

    findings = relationship("Finding", back_populates="pattern")
    references = relationship("VulnerabilityReference", secondary=pattern_references, back_populates="patterns")

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    function_id = Column(Integer, ForeignKey("functions.id"))
    pattern_id = Column(Integer, ForeignKey("patterns.id"), nullable=True)
    severity = Column(String)
    confidence = Column(Float)
    evidence = Column(Text)
    recommendation = Column(Text)
    ai_analysis = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    resolved = Column(Boolean, default=False)

    function = relationship("Function", back_populates="findings")
    pattern = relationship("Pattern", back_populates="findings")
    ai_analyses = relationship("AIAnalysis", back_populates="finding")
    references = relationship("VulnerabilityReference", secondary=finding_references, back_populates="findings")

class Payload(Base):
    __tablename__ = "payloads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String)
    base_code = Column(Text)
    morph_config = Column(JSON)
    target_function_id = Column(Integer, ForeignKey("functions.id"), nullable=True)
    target_device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    result = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    target_function = relationship("Function", back_populates="payloads")
    target_device = relationship("Device", back_populates="payloads")
    variants = relationship("Variant", back_populates="payload")
    ai_analyses = relationship("AIAnalysis", back_populates="payload")

class Variant(Base):
    __tablename__ = "variants"

    id = Column(Integer, primary_key=True, index=True)
    payload_id = Column(Integer, ForeignKey("payloads.id"))
    morph_hash = Column(String)
    code = Column(Text)
    result = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    payload = relationship("Payload", back_populates="variants")

class ExploitChain(Base):
    __tablename__ = "exploit_chains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    steps = Column(JSON)  # Array of step IDs
    target_device_id = Column(Integer, ForeignKey("devices.id"))
    target_function_id = Column(Integer, ForeignKey("functions.id"))
    result = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    target_device = relationship("Device", back_populates="exploit_chains")
    target_function = relationship("Function", back_populates="exploit_chains")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    type = Column(String)
    info = Column(JSON)
    connected = Column(Boolean)
    last_seen = Column(DateTime)
    notes = Column(Text)

    device = relationship("Device", back_populates="sessions")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String)
    format = Column(String)
    content = Column(Text)
    generated_at = Column(DateTime, server_default=func.now())
    notes = Column(Text)

    project = relationship("Project", back_populates="reports")

class AIModel(Base):
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    api_key = Column(String)  # Should be encrypted in a real app
    base_url = Column(String)
    enabled = Column(Boolean, default=True)
    notes = Column(Text)

    ai_analyses = relationship("AIAnalysis", back_populates="ai_model")

class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id"), nullable=True)
    function_id = Column(Integer, ForeignKey("functions.id"), nullable=True)
    payload_id = Column(Integer, ForeignKey("payloads.id"), nullable=True)
    ai_model_id = Column(Integer, ForeignKey("ai_models.id"))
    prompt = Column(Text)
    response = Column(Text)
    confidence = Column(Float)
    created_at = Column(DateTime, server_default=func.now())

    finding = relationship("Finding", back_populates="ai_analyses")
    function = relationship("Function", back_populates="ai_analyses")
    payload = relationship("Payload", back_populates="ai_analyses")
    ai_model = relationship("AIModel", back_populates="ai_analyses")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)  # admin, analyst, read_only
    created_at = Column(DateTime, server_default=func.now())

    logs = relationship("Log", back_populates="user")

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String)
    target = Column(Text)
    result = Column(String)
    timestamp = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="logs")

class ExternalSource(Base):
    __tablename__ = "external_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String)
    description = Column(Text)
    type = Column(String)  # exploit_db, cve_db, poc_repo, etc.
    created_at = Column(DateTime, server_default=func.now())

    references = relationship("VulnerabilityReference", back_populates="source")

class VulnerabilityReference(Base):
    __tablename__ = "vulnerability_references"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("external_sources.id"))
    external_id = Column(String, index=True)  # e.g., CVE-2021-1234, EDB-ID 12345
    url = Column(String)
    description = Column(Text)
    severity = Column(String)
    cvss_score = Column(Float)
    created_at = Column(DateTime, server_default=func.now())

    source = relationship("ExternalSource", back_populates="references")
    findings = relationship("Finding", secondary=finding_references, back_populates="references")
    patterns = relationship("Pattern", secondary=pattern_references, back_populates="references")
