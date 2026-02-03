from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import projects, devices, analysis, payloads, recon, credentials, reports, exploit_db, exploit_chains, diffing, assets, firmware, source, console, fuzzing, bruteforce, cloning, web_testing, phishing, cracking, weaponization, emulation, hardware, settings, compiler, ai_engine, snippets, automation
import os

app = FastAPI(title="Offensive Security Platform")

# Mount static files
os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
os.makedirs("app/templates", exist_ok=True)
templates = Jinja2Templates(directory="app/templates")

# Include API routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(payloads.router, prefix="/api/payloads", tags=["payloads"])
app.include_router(recon.router, prefix="/api/recon", tags=["recon"])
app.include_router(credentials.router, prefix="/api/credentials", tags=["credentials"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(exploit_db.router, prefix="/api/exploit-db", tags=["exploit-db"])
app.include_router(exploit_chains.router, prefix="/api/exploit-chains", tags=["exploit-chains"])
app.include_router(diffing.router, prefix="/api/diffing", tags=["diffing"])
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(firmware.router, prefix="/api/firmware", tags=["firmware"])
app.include_router(source.router, prefix="/api/source", tags=["source"])
app.include_router(console.router, prefix="/api/console", tags=["console"])
app.include_router(fuzzing.router, prefix="/api/fuzzing", tags=["fuzzing"])
app.include_router(bruteforce.router, prefix="/api/bruteforce", tags=["bruteforce"])
app.include_router(cloning.router, prefix="/api/cloning", tags=["cloning"])
app.include_router(web_testing.router, prefix="/api/web-testing", tags=["web-testing"])
app.include_router(phishing.router, prefix="/api/phishing", tags=["phishing"])
app.include_router(cracking.router, prefix="/api/cracking", tags=["cracking"])
app.include_router(weaponization.router, prefix="/api/weaponization", tags=["weaponization"])
app.include_router(emulation.router, prefix="/api/emulation", tags=["emulation"])
app.include_router(hardware.router, prefix="/api/hardware", tags=["hardware"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(compiler.router, prefix="/api/compiler", tags=["compiler"])
app.include_router(ai_engine.router, prefix="/api/ai-engine", tags=["ai-engine"])
app.include_router(snippets.router, prefix="/api/snippets", tags=["snippets"])
app.include_router(automation.router, prefix="/api/automation", tags=["automation"])

@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
