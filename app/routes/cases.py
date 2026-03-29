from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from pathlib import Path
from app.core.database import get_session
from app.models.case_study import CaseStudy
from app.models.case_session import CaseStudySession

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

router = APIRouter(prefix="/cases", tags=["cases"])

@router.get("")
def case_library(request: Request, session: Session = Depends(get_session)):
    cases = session.exec(select(CaseStudy)).all()
    return templates.TemplateResponse(
        request=request, 
        name="cases/library.html", 
        context={"cases": cases}
    )

@router.post("/{case_id}/start")
def start_session(case_id: int, request: Request, session: Session = Depends(get_session)):
    # Create a new session for this case
    new_session = CaseStudySession(case_study_id=case_id, status="in_progress", current_stage=1)
    session.add(new_session)
    session.commit()
    session.refresh(new_session)
    
    # Redirect to the session player
    return RedirectResponse(url=f"/session/{new_session.id}", status_code=303)