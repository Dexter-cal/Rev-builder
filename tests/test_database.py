import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.models.models import Project, Device

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_create_project_with_device(db):
    # Create a project
    project = Project(
        name="Test Project",
        description="A test project",
        status="active",
        authorized_targets=["192.168.1.1"]
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    assert project.id is not None
    assert project.name == "Test Project"

    # Create a device
    device = Device(
        project_id=project.id,
        name="Test Router",
        type="router",
        ip="192.168.1.1"
    )
    db.add(device)
    db.commit()
    db.refresh(device)

    assert device.id is not None
    assert device.project_id == project.id
    assert len(project.devices) == 1
    assert project.devices[0].name == "Test Router"

def test_json_field(db):
    project = Project(
        name="JSON Test",
        authorized_targets=["target1", "target2"]
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    assert isinstance(project.authorized_targets, list)
    assert "target1" in project.authorized_targets

from app.models.models import Finding, ExternalSource, VulnerabilityReference

def test_vulnerability_references(db):
    # Get a seeded source
    source = db.query(ExternalSource).filter(ExternalSource.name == "Exploit-DB").first()
    if not source:
        source = ExternalSource(name="Exploit-DB", type="exploit_db")
        db.add(source)
        db.commit()

    # Create a reference
    ref = VulnerabilityReference(
        source_id=source.id,
        external_id="EDB-ID-12345",
        url="https://www.exploit-db.com/exploits/12345"
    )
    db.add(ref)

    # Create a finding (need a function first)
    from app.models.models import Project, Device, Binary, Function
    project = Project(name="Ref Test")
    db.add(project)
    db.commit()
    device = Device(project_id=project.id, name="Device")
    db.add(device)
    db.commit()
    binary = Binary(device_id=device.id, path="/bin/ls")
    db.add(binary)
    db.commit()
    func = Function(binary_id=binary.id, name="main")
    db.add(func)
    db.commit()

    finding = Finding(function_id=func.id, severity="high")
    finding.references.append(ref)
    db.add(finding)
    db.commit()
    db.refresh(finding)

    assert len(finding.references) == 1
    assert finding.references[0].external_id == "EDB-ID-12345"
    assert len(ref.findings) == 1
