import click
from app.database.session import SessionLocal
from app.models import models
from tabulate import tabulate # I should probably install this for nice tables

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

@cli.group()
def analyze():
    """Binary analysis commands"""
    pass

@analyze.command(name="binary")
@click.argument("path")
def analyze_binary(path):
    """Scan a binary for vulnerabilities (Simulation)"""
    click.echo(f"Analyzing binary at {path}...")
    # In a real app, this would call analysis logic
    click.echo(click.style("CRITICAL: unsafe gets() detected at 0x401240", fg="red", bold=True))

if __name__ == "__main__":
    cli()
