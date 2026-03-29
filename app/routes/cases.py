from fastapi import APIRouter, Request, Depends, HTTPException
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
    
    display_cases = []
    for c in cases:
        # Map difficulty to user-friendly badge
        if c.difficulty in [1, 2]:
            diff_label = "Easy"
            diff_class = "easy"
        elif c.difficulty == 3:
            diff_label = "Moderate"
            diff_class = "moderate"
        elif c.difficulty in [4, 5]:
            diff_label = "Hard"
            diff_class = "hard"
        else:
            diff_label = "Unknown"
            diff_class = "moderate"
            
        display_cases.append({
            "id": c.id,
            "title": c.title,
            "specialty": c.specialty,
            "difficulty_num": c.difficulty,
            "difficulty_label": diff_label,
            "difficulty_class": diff_class,
            "summary": c.summary
        })

    return templates.TemplateResponse(
        request=request, 
        name="cases/library.html", 
        context={
            "cases": display_cases,
            "case_count": len(display_cases)
        }
    )

@router.post("/{case_id}/start")
def start_session(case_id: int, request: Request, session: Session = Depends(get_session)):
    # Validate case exists
    case_study = session.get(CaseStudy, case_id)
    if not case_study:
        raise HTTPException(status_code=404, detail="Case not found")

    # Create a new session for this case
    new_session = CaseStudySession(case_study_id=case_id, status="in_progress", current_stage=1)
    session.add(new_session)
    session.commit()
    session.refresh(new_session)
    
    # Redirect to the session player
    return RedirectResponse(url=f"/session/{new_session.id}", status_code=303)