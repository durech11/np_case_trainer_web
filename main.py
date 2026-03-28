from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from core.database import create_db_and_tables

BASE_DIR = Path(__file__).resolve().parent

# Ensure essential directories exist
for directory in ["static", "templates", "core", "models", "db", "cases"]:
    (BASE_DIR / directory).mkdir(exist_ok=True)

app = FastAPI(title="NP Case Trainer", description="Educational clinical reasoning trainer")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "NP Case Trainer"}

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})