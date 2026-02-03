import click
from app.database.session import SessionLocal
from app.models import models
from app.services.analysis_service import AnalysisService
from app.services.exploit_service import ExploitService
from tabulate import tabulate

def get_db():
    return SessionLocal()

@click.group()
def cli():
    """Offensive Security Platform CLI"""
    pass

@cli.group()
def projects():
    """Manage projects"""
    pass

@projects.command(name="list")
def list_projects():
    """List all projects"""
    db = get_db()
    projects = db.query(models.Project).all()
    data = [[p.id, p.name, p.status] for p in projects]
    click.echo(tabulate(data, headers=["ID", "Name", "Status"]))
    db.close()

@projects.command(name="create")
@click.argument("name")
@click.option("--description", "-d", help="Project description")
def create_project(name, description):
    """Create a new project"""
    db = get_db()
    project = models.Project(name=name, description=description, status="planning")
    db.add(project)
    db.commit()
    click.echo(f"Project '{name}' created with ID {project.id}")
    db.close()

@cli.group()
def devices():
    """Manage devices"""
    pass

@devices.command(name="list")
@click.option("--project-id", type=int, help="Filter by project ID")
def list_devices(project_id):
    """List all devices"""
    db = get_db()
    query = db.query(models.Device)
    if project_id:
        query = query.filter(models.Device.project_id == project_id)
    devices = query.all()
    data = [[d.id, d.name, d.ip, d.type] for d in devices]
    click.echo(tabulate(data, headers=["ID", "Name", "IP", "Type"]))
    db.close()

@devices.command(name="create")
@click.argument("project-id", type=int)
@click.argument("name")
@click.option("--ip", help="IP address")
def create_device(project_id, name, ip):
    """Create a new device"""
    db = get_db()
    device = models.Device(project_id=project_id, name=name, ip=ip, type="server")
    db.add(device)
    db.commit()
    click.echo(f"Device '{name}' created with ID {device.id}")
    db.close()

@cli.group()
def analyze():
    """Binary analysis commands"""
    pass

@analyze.command(name="binary")
@click.argument("device-id", type=int)
@click.argument("path")
def analyze_binary(device_id, path):
    """Ingest and scan a binary for vulnerabilities"""
    db = get_db()
    click.echo(f"Ingesting binary from device {device_id} at {path}...")
    binary = AnalysisService.simulate_binary_ingestion(db, device_id, path)
    click.echo(f"Binary ingested with ID {binary.id}. Discovered {len(binary.functions)} functions.")

    click.echo("Scanning for vulnerability patterns...")
    findings_count = AnalysisService.scan_binary(db, binary.id)

    if findings_count > 0:
        click.echo(click.style(f"SUCCESS: Found {findings_count} vulnerabilities!", fg="red", bold=True))
        # List findings
        findings = db.query(models.Finding).join(models.Function).filter(models.Function.binary_id == binary.id).all()
        data = [[f.id, f.function.name, f.severity, f.confidence] for f in findings]
        click.echo(tabulate(data, headers=["ID", "Function", "Severity", "Confidence"]))
    else:
        click.echo("No vulnerabilities found.")
    db.close()

@cli.group()
def exploit():
    """Exploitation commands"""
    pass

@exploit.command(name="generate")
@click.argument("finding-id", type=int)
@click.option("--name", "-n", default="exploit_v1", help="Payload name")
def generate_exploit(finding_id, name):
    """Generate a payload for a specific finding"""
    db = get_db()
    click.echo(f"Generating payload for finding {finding_id}...")
    payload = ExploitService.generate_payload(db, finding_id, name)
    if payload:
        click.echo(click.style(f"Payload generated: {payload.name} (ID: {payload.id})", fg="green"))
        click.echo("Base code:")
        click.echo(payload.base_code)
    else:
        click.echo(click.style("Error: Finding not found", fg="red"))
    db.close()

if __name__ == "__main__":
    cli()
