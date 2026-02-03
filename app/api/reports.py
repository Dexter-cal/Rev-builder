from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import models
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

router = APIRouter()

@router.post("/{project_id}/generate")
def generate_report(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    reports_dir = "generated_reports"
    os.makedirs(reports_dir, exist_ok=True)
    report_filename = f"report_{project.id}_{os.urandom(4).hex()}.pdf"
    report_path = os.path.join(reports_dir, report_filename)

    # Gather data
    devices = db.query(models.Device).filter(models.Device.project_id == project_id).all()

    # Create PDF
    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, height - 50, f"Security Assessment Report: {project.name}")

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 80, f"Project Description: {project.description}")

    y = height - 120
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y, "Assets and Findings")
    y -= 20

    for device in devices:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(120, y, f"Device: {device.name} ({device.ip})")
        y -= 15

        for binary in device.binaries:
            for func in binary.functions:
                if func.danger_score > 50:
                    c.setFont("Helvetica", 10)
                    c.drawString(140, y, f"- Vulnerable function: {func.name} (Score: {func.danger_score})")
                    y -= 12
                    if y < 50:
                        c.showPage()
                        y = height - 50
        y -= 10

    c.save()

    report = models.Report(
        project_id=project_id,
        title=f"Report - {project.name}",
        format="pdf",
        content=report_path # Store path in content for this prototype
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.get("/download/{report_id}")
def download_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report or not os.path.exists(report.content):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(report.content, filename=os.path.basename(report.content), media_type='application/pdf')

@router.get("/{project_id}")
def get_reports(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.Report).filter(models.Report.project_id == project_id).all()
