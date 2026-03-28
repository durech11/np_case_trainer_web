from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from pathlib import Path
from app.core.database import init_db, get_session
from app.models.case_study import CaseStudy

# BASE_DIR is now the project root (one level up from app/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure essential directories exist at the project root
for directory in ["static", "templates", "db", "cases"]:
    (BASE_DIR / directory).mkdir(exist_ok=True)

app = FastAPI(title="NP Case Trainer", description="Educational clinical reasoning trainer")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "NP Case Trainer"}

@app.get("/")
def read_root(request: Request, session: Session = Depends(get_session)):
    # Test DB query to verify initialization works
    cases = session.exec(select(CaseStudy)).all()
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"case_count": len(cases)}
    )