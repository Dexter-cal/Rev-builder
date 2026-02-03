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
