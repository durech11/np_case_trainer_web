from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from pathlib import Path
from app.core.database import get_session
from app.models.case_session import CaseStudySession

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

router = APIRouter(prefix="/session", tags=["session"])

@router.get("/{session_id}")
def session_player(session_id: int, request: Request, session: Session = Depends(get_session)):
    # Simply render a placeholder for now
    case_session = session.get(CaseStudySession, session_id)
    if not case_session:
        return templates.TemplateResponse(
            request=request, 
            name="error.html", 
            context={"message": "Session not found"}
        )
        
    return templates.TemplateResponse(
        request=request, 
        name="session/player.html", 
        context={"session": case_session}
    )