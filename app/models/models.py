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

device_tags = Table(
    "device_tags",
    Base.metadata,
    Column("device_id", Integer, ForeignKey("devices.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

function_tags = Table(
    "function_tags",
    Base.metadata,
    Column("function_id", Integer, ForeignKey("functions.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
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
    zero_click_enabled = Column(Boolean, default=False)
    notes = Column(Text)

    devices = relationship("Device", back_populates="project")
    reports = relationship("Report", back_populates="project")
    attack_surfaces = relationship("AttackSurface", back_populates="project")

class ProjectTemplate(Base):
    __tablename__ = "project_templates"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    config = Column(JSON)  # Default targets, tools, etc.

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
    tags = relationship("Tag", secondary=device_tags, back_populates="devices")
    credentials = relationship("Credential", back_populates="device")

class Binary(Base):
    __tablename__ = "binaries"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    path = Column(String)
    hash = Column(String)  # SHA-256
    arch = Column(String)  # x86, ARM, etc.
    file_type = Column(String)  # ELF, PE, Mach-O, DEX, firmware
    size = Column(Integer)
    protections = Column(JSON) # e.g., {"NX": True, "ASLR": True, "Canary": False}
    created_at = Column(DateTime, server_default=func.now())
    notes = Column(Text)

    device = relationship("Device", back_populates="binaries")
    functions = relationship("Function", back_populates="binary")

class FirmwareDiff(Base):
    __tablename__ = "firmware_diffs"
    id = Column(Integer, primary_key=True)
    binary_a_id = Column(Integer, ForeignKey("binaries.id"))
    binary_b_id = Column(Integer, ForeignKey("binaries.id"))
    diff_data = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

class Function(Base):
    __tablename__ = "functions"

    id = Column(Integer, primary_key=True, index=True)
    binary_id = Column(Integer, ForeignKey("binaries.id"))
    name = Column(String)
    offset = Column(String)
    size = Column(Integer)
    hash = Column(String) # SHA-256 of function body
    danger_score = Column(Integer)  # 0-100
    vuln_type = Column(String)
    is_zero_click_candidate = Column(Boolean, default=False)
    surface_type = Column(String) # messaging, notification, background_service, media_parser
    assembly_snippet = Column(Text)
    python_like = Column(Text)
    notes = Column(Text)

    binary = relationship("Binary", back_populates="functions")
    findings = relationship("Finding", back_populates="function")
    payloads = relationship("Payload", back_populates="target_function")
    exploit_chains = relationship("ExploitChain", back_populates="target_function")
    ai_analyses = relationship("AIAnalysis", back_populates="function")
    tags = relationship("Tag", secondary=function_tags, back_populates="functions")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    color = Column(String)  # CSS color or hex

    devices = relationship("Device", secondary=device_tags, back_populates="tags")
    functions = relationship("Function", secondary=function_tags, back_populates="tags")

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
    risk_score = Column(Integer)  # Composite score 0-100
    created_at = Column(DateTime, server_default=func.now())
    resolved = Column(Boolean, default=False)

    function = relationship("Function", back_populates="findings")
    pattern = relationship("Pattern", back_populates="findings")
    ai_analyses = relationship("AIAnalysis", back_populates="finding")
    references = relationship("VulnerabilityReference", secondary=finding_references, back_populates="findings")
    evidence_files = relationship("Evidence", back_populates="finding")

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
    is_template = Column(Boolean, default=False)
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
    snapshots = relationship("SessionSnapshot", back_populates="session")

class SessionSnapshot(Base):
    __tablename__ = "session_snapshots"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    timestamp = Column(DateTime, server_default=func.now())
    process_list = Column(JSON)
    network_connections = Column(JSON)
    filesystem_delta = Column(JSON)

    session = relationship("Session", back_populates="snapshots")

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
    model_type = Column(String) # LLM, Embedding, CodeGen
    api_key = Column(String)
    base_url = Column(String)
    enabled = Column(Boolean, default=True)
    profile_config = Column(JSON) # e.g., {"temperature": 0.7, "top_p": 0.9}
    custom_args = Column(JSON) # e.g., {"max_tokens": 2048}
    notes = Column(Text)

    ai_analyses = relationship("AIAnalysis", back_populates="ai_model")

class VulnerabilityMap(Base):
    __tablename__ = "vulnerability_map"
    id = Column(Integer, primary_key=True)
    software_name = Column(String, index=True)
    version_range = Column(String)
    cve_id = Column(String, index=True)
    description = Column(Text)
    exploit_module_id = Column(Integer, ForeignKey("exploit_modules.id"), nullable=True)

    exploit_module = relationship("ExploitModule", back_populates="vuln_mappings")

class ExploitModule(Base):
    __tablename__ = "exploit_modules"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True) # e.g., "linux/http/apache_struts_rce"
    description = Column(Text)
    author = Column(String)
    platform = Column(String) # linux, windows, ios, etc.
    arch = Column(JSON) # ["x86", "arm"]
    options = Column(JSON) # {"RHOST": {"required": True, "desc": "Target IP"}, ...}
    payload_type = Column(String) # cmd, meterpreter, reverse_tcp
    script_path = Column(String) # path to actual python script

    vuln_mappings = relationship("VulnerabilityMap", back_populates="exploit_module")

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
    accepted = Column(Boolean, nullable=True)
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

class FuzzingJob(Base):
    __tablename__ = "fuzzing_jobs"
    id = Column(Integer, primary_key=True)
    binary_id = Column(Integer, ForeignKey("binaries.id"))
    target_function_id = Column(Integer, ForeignKey("functions.id"), nullable=True)
    status = Column(String) # pending, running, completed, failed
    config = Column(JSON) # e.g. {"engine": "libfuzzer", "timeout": 3600}
    created_at = Column(DateTime, server_default=func.now())

    results = relationship("FuzzingResult", back_populates="job")

class FuzzingResult(Base):
    __tablename__ = "fuzzing_results"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("fuzzing_jobs.id"))
    input_data = Column(Text) # input that caused the crash
    crash_log = Column(Text)
    stack_trace = Column(Text)
    severity = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    job = relationship("FuzzingJob", back_populates="results")

class BruteforceJob(Base):
    __tablename__ = "bruteforce_jobs"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    service = Column(String) # ssh, telnet, http_basic, etc.
    status = Column(String)
    config = Column(JSON) # e.g. {"wordlist": "common.txt", "threads": 10}
    created_at = Column(DateTime, server_default=func.now())

    results = relationship("BruteforceResult", back_populates="job")

class BruteforceResult(Base):
    __tablename__ = "bruteforce_results"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("bruteforce_jobs.id"))
    username = Column(String)
    password = Column(String)
    success = Column(Boolean)
    response_code = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    job = relationship("BruteforceJob", back_populates="results")

class CloningJob(Base):
    __tablename__ = "cloning_jobs"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    channel = Column(String) # usb, network, wifi, bluetooth, drag_drop
    source_info = Column(String) # IP, MAC, Serial, etc.
    status = Column(String)
    binary_id = Column(Integer, ForeignKey("binaries.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class WebProxyRequest(Base):
    __tablename__ = "web_proxy_requests"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    method = Column(String)
    url = Column(String)
    headers = Column(JSON)
    body = Column(Text)
    response_code = Column(Integer)
    response_body = Column(Text)
    captured_at = Column(DateTime, server_default=func.now())

class PhishingCampaign(Base):
    __tablename__ = "phishing_campaigns"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    template = Column(String) # login_page, survey, download
    status = Column(String) # active, completed
    clicks = Column(Integer, default=0)
    submissions = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

class CrackingJob(Base):
    __tablename__ = "cracking_jobs"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    hash_type = Column(String) # NTLM, MD5, SHA256
    hashes = Column(JSON) # List of hashes to crack
    status = Column(String)
    results = Column(JSON) # List of cracked passwords
    created_at = Column(DateTime, server_default=func.now())

class CompilerJob(Base):
    __tablename__ = "compiler_jobs"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    type = Column(String) # compile, decompile, modify
    source_code = Column(Text)
    output_binary_id = Column(Integer, ForeignKey("binaries.id"), nullable=True)
    status = Column(String)
    logs = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class WeaponizationJob(Base):
    __tablename__ = "weaponization_jobs"
    id = Column(Integer, primary_key=True)
    finding_id = Column(Integer, ForeignKey("findings.id"))
    target_platform = Column(String) # linux, windows, embedded
    exploit_type = Column(String) # metasploit_module, python_script, c_source
    code = Column(Text)
    status = Column(String)
    created_at = Column(DateTime, server_default=func.now())

class EmulationJob(Base):
    __tablename__ = "emulation_jobs"
    id = Column(Integer, primary_key=True)
    binary_id = Column(Integer, ForeignKey("binaries.id"))
    engine = Column(String) # qemu, unicorn, bochs
    status = Column(String)
    traces = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

class HardwareJob(Base):
    __tablename__ = "hardware_jobs"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    interface = Column(String) # jtag, swd, uart, spi, i2c, sdr
    action = Column(String) # sniff, dump, fuzz, glitch
    data_captured = Column(JSON)
    status = Column(String)
    created_at = Column(DateTime, server_default=func.now())

class HardwareInterface(Base):
    __tablename__ = "hardware_interfaces"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    type = Column(String)  # UART, JTAG, SPI, I2C, USB, GPIO
    pins = Column(JSON)    # e.g., {"TX": 1, "RX": 2} or {"TDI": 5, ...}
    voltage = Column(Float) # 1.8, 3.3, 5.0
    baud_rate = Column(Integer, nullable=True)
    notes = Column(Text)
    discovered_at = Column(DateTime, server_default=func.now())

class FirmwareImage(Base):
    __tablename__ = "firmware_images"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    binary_id = Column(Integer, ForeignKey("binaries.id"), nullable=True)
    version = Column(String)
    file_path = Column(String) # Path to the raw .bin/.img file
    extraction_path = Column(String) # Path to the extracted filesystem
    hash = Column(String)
    size = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    notes = Column(Text)

class FirmwareAnalysis(Base):
    __tablename__ = "firmware_analyses"
    id = Column(Integer, primary_key=True)
    firmware_id = Column(Integer, ForeignKey("firmware_images.id"))
    tool_name = Column(String) # binwalk, emba, firmwalker
    results = Column(JSON)     # Detailed findings
    report_path = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class RecompilationJob(Base):
    __tablename__ = "recompilation_jobs"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    binary_id = Column(Integer, ForeignKey("binaries.id"), nullable=True)
    source_code = Column(Text)
    patch_diff = Column(Text, nullable=True)
    target_arch = Column(String)
    compiler_flags = Column(String)
    status = Column(String) # pending, compiling, success, failed
    logs = Column(Text)
    output_binary_id = Column(Integer, ForeignKey("binaries.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class PayloadSuccessRate(Base):
    __tablename__ = "payload_success_rates"
    id = Column(Integer, primary_key=True)
    payload_id = Column(Integer, ForeignKey("payloads.id"))
    arch = Column(String)
    os = Column(String)
    success_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    crash_count = Column(Integer, default=0)
    notes = Column(Text)

class WorkflowNode(Base):
    __tablename__ = "workflow_nodes"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    type = Column(String) # target, finding, payload, session, hardware, clone
    reference_id = Column(Integer) # ID of the actual object
    pos_x = Column(Float)
    pos_y = Column(Float)
    data = Column(JSON) # Additional UI state

class WorkflowEdge(Base):
    __tablename__ = "workflow_edges"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    source_node_id = Column(Integer, ForeignKey("workflow_nodes.id"))
    target_node_id = Column(Integer, ForeignKey("workflow_nodes.id"))
    type = Column(String) # exploits, contains, based_on, triggers

class ProjectState(Base):
    __tablename__ = "project_states"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    state_data = Column(JSON) # Snapshot of interesting tables or project metadata
    timestamp = Column(DateTime, server_default=func.now())

class ActionHistory(Base):
    __tablename__ = "action_history"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    action_type = Column(String)
    description = Column(Text)
    undo_data = Column(JSON) # Data needed to revert the action
    redo_data = Column(JSON) # Data needed to re-apply the action
    timestamp = Column(DateTime, server_default=func.now())

class InjectionSnippet(Base):
    __tablename__ = "injection_snippets"
    id = Column(Integer, primary_key=True)
    category = Column(String) # SQLi, XSS, CmdInj, FormatStr, Shellcode
    name = Column(String)
    content = Column(Text)
    description = Column(Text)
    platform = Column(String)
    created_at = Column(DateTime, server_default=func.now())

class FindingScore(Base):
    __tablename__ = "finding_scores"
    id = Column(Integer, primary_key=True)
    finding_id = Column(Integer, ForeignKey("findings.id"))
    exploitability = Column(Float) # 0-1
    impact = Column(Float) # 0-1
    composite_score = Column(Float)
    priority = Column(String) # critical, high, medium, low
    notes = Column(Text)

class ProjectCollaborator(Base):
    __tablename__ = "project_collaborators"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String) # owner, analyst, viewer
    status = Column(String) # online, offline

class NodeComment(Base):
    __tablename__ = "node_comments"
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey("workflow_nodes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    timestamp = Column(DateTime, server_default=func.now())

class AutomationTrigger(Base):
    __tablename__ = "automation_triggers"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    event_type = Column(String) # on_new_target, on_finding, on_payload_success
    action_type = Column(String) # scan, fuzz, report, notify
    config = Column(JSON)
    enabled = Column(Boolean, default=True)

class Playbook(Base):
    __tablename__ = "playbooks"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    workflow_data = Column(JSON) # Serialized nodes and edges
    category = Column(String) # Firmware, Web, Hardware, Network
    is_community = Column(Boolean, default=False)

class ProjectCommit(Base):
    __tablename__ = "project_commits"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    diff_data = Column(JSON)
    timestamp = Column(DateTime, server_default=func.now())

class ThreatModel(Base):
    __tablename__ = "threat_models"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    graph_data = Column(JSON) # Assets, threats, mitigations
    risk_summary = Column(Text)
    last_updated = Column(DateTime, server_default=func.now())

class DecompilationJob(Base):
    __tablename__ = "decompilation_jobs"
    id = Column(Integer, primary_key=True)
    binary_id = Column(Integer, ForeignKey("binaries.id"))
    status = Column(String) # pending, in_progress, completed, failed
    source_output = Column(Text)
    logs = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class DeploymentJob(Base):
    __tablename__ = "deployment_jobs"
    id = Column(Integer, primary_key=True)
    binary_id = Column(Integer, ForeignKey("binaries.id"))
    target_device_id = Column(Integer, ForeignKey("devices.id"))
    target_type = Column(String) # real, clone, copy
    status = Column(String) # pending, deploying, success, failed
    deployment_path = Column(String) # Path on the target device
    logs = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class FunctionCall(Base):
    __tablename__ = "function_calls"
    id = Column(Integer, primary_key=True)
    caller_id = Column(Integer, ForeignKey("functions.id"))
    callee_id = Column(Integer, ForeignKey("functions.id"), nullable=True)
    callee_name = Column(String) # For external/unresolved calls
    offset = Column(String) # Offset of the call instruction
    is_indirect = Column(Boolean, default=False)

class SystemConfig(Base):
    __tablename__ = "system_configs"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    value = Column(JSON)
    description = Column(Text)

class ExploitWeapon(Base):
    __tablename__ = "exploit_weapons"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    code = Column(Text)
    language = Column(String) # python, c, bash
    target_arch = Column(String)
    compiled_binary_path = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class CodeSnippet(Base):
    __tablename__ = "code_snippets"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    language = Column(String)
    tags = Column(JSON) # e.g., ["buffer_overflow", "tutorial"]
    category = Column(String) # Learning, Template, Exploit
    created_at = Column(DateTime, server_default=func.now())

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    id = Column(Integer, primary_key=True)
    topic = Column(String)
    content = Column(Text)
    references = Column(JSON)
    last_updated = Column(DateTime, server_default=func.now())

class Credential(Base):
    __tablename__ = "credentials"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    username = Column(String)
    password = Column(String)
    type = Column(String)  # ssh, web, hash, private_key
    origin = Column(String)  # how it was found

    device = relationship("Device", back_populates="credentials")

class AttackSurface(Base):
    __tablename__ = "attack_surfaces"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    ip = Column(String)
    port = Column(Integer)
    protocol = Column(String)
    service = Column(String)
    version = Column(String)
    vuln_info = Column(Text)

    project = relationship("Project", back_populates="attack_surfaces")

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True)
    finding_id = Column(Integer, ForeignKey("findings.id"))
    file_path = Column(String)
    description = Column(Text)
    type = Column(String)  # screenshot, log, pcap

    finding = relationship("Finding", back_populates="evidence_files")

class NetworkNode(Base):
    __tablename__ = "network_nodes"
    id = Column(Integer, primary_key=True)
    label = Column(String)
    type = Column(String)  # router, pc, server, iot

class NetworkEdge(Base):
    __tablename__ = "network_edges"
    id = Column(Integer, primary_key=True)
    source_node_id = Column(Integer, ForeignKey("network_nodes.id"))
    target_node_id = Column(Integer, ForeignKey("network_nodes.id"))
    type = Column(String)  # ethernet, wifi, vpn

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
    external_id = Column(String, index=True)
    url = Column(String)
    description = Column(Text)
    severity = Column(String)
    cvss_score = Column(Float)
    created_at = Column(DateTime, server_default=func.now())

    source = relationship("ExternalSource", back_populates="references")
    findings = relationship("Finding", secondary=finding_references, back_populates="references")
    patterns = relationship("Pattern", secondary=pattern_references, back_populates="references")

class Wordlist(Base):
    __tablename__ = "wordlists"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    content = Column(Text) # The actual wordlist items
    category = Column(String) # passwords, usernames, subdomains, etc.
    is_ai_generated = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
