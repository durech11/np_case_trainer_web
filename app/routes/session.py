from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from pathlib import Path
from app.core.database import get_session
from app.models.case_session import CaseStudySession
from app.models.case_study import CaseStudy
from app.models.schemas import CaseStudySchema

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

router = APIRouter(prefix="/session", tags=["session"])

@router.get("/{session_id}")
def session_player(session_id: int, request: Request, session: Session = Depends(get_session)):
    case_session = session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    case_study = session.get(CaseStudy, case_session.case_study_id)
    if not case_study:
        raise HTTPException(status_code=404, detail="Case study not found for this session")

    # Parse JSON into structured Pydantic schema
    case_data = CaseStudySchema.model_validate_json(case_study.raw_json)
        
    return templates.TemplateResponse(
        request=request, 
        name="session/player.html", 
        context={
            "session": case_session,
            "case": case_data
        }
    )