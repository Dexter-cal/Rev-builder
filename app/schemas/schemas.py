from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, Any

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = "planning"
    authorized_targets: Optional[List[str]] = []
    notes: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class DeviceBase(BaseModel):
    project_id: int
    name: str
    type: Optional[str] = None
    os: Optional[str] = None
    firmware_version: Optional[str] = None
    ip: Optional[str] = None
    mac: Optional[str] = None
    serial: Optional[str] = None
    last_seen: Optional[datetime] = None
    notes: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class Device(DeviceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
