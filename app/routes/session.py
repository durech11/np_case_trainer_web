from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from pathlib import Path
from datetime import datetime, timezone

from app.core.database import get_session, engine
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

    case_data = CaseStudySchema.model_validate_json(case_study.raw_json)
    
    context = {
        "request": request,
        "session": case_session,
        "case": case_data,
    }

    # If at the final stage, perform differential diagnosis comparison
    if case_session.current_stage == 5:
        user_dx_set = {dx.strip().lower() for dx in case_session.user_differential_diagnosis}
        model_dx_set = {dx.diagnosis.strip().lower() for dx in case_data.model_differential}
        
        correct_matches = [dx for dx in case_session.user_differential_diagnosis if dx.strip().lower() in model_dx_set]
        extra_diagnoses = [dx for dx in case_session.user_differential_diagnosis if dx.strip().lower() not in model_dx_set]
        missed_diagnoses = [dx.diagnosis for dx in case_data.model_differential if dx.diagnosis.strip().lower() not in user_dx_set]
        
        context["review"] = {
            "correct_matches": correct_matches,
            "extra_diagnoses": extra_diagnoses,
            "missed_diagnoses": missed_diagnoses
        }
        
    return templates.TemplateResponse(
        request=request,
        name="session/player.html",
        context=context
    )

@router.post("/{session_id}/next")
def next_stage(session_id: int, session: Session = Depends(get_session)):
    case_session = session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if case_session.current_stage < 5:
        case_session.current_stage += 1
        case_session.updated_at = datetime.now(timezone.utc)
        session.add(case_session)
        session.commit()
    
    # Mark as complete if reaching the final stage
    if case_session.current_stage == 5 and not case_session.completed_at:
        case_session.status = "completed"
        case_session.completed_at = datetime.now(timezone.utc)
        session.add(case_session)
        session.commit()

    return RedirectResponse(url=f"/session/{session_id}", status_code=303)

@router.post("/{session_id}/prev")
def prev_stage(session_id: int, session: Session = Depends(get_session)):
    case_session = session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if case_session.current_stage > 1:
        case_session.current_stage -= 1
        case_session.updated_at = datetime.now(timezone.utc)
        session.add(case_session)
        session.commit()
        
    return RedirectResponse(url=f"/session/{session_id}", status_code=303)

@router.post("/{session_id}/ddx/add")
def add_ddx(session_id: int, diagnosis: str = Form(...), db_session: Session = Depends(get_session)):
    case_session = db_session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    new_dx = diagnosis.strip()
    if new_dx:
        # Case-insensitive check for duplicates
        existing_lower = [dx.lower() for dx in case_session.user_differential_diagnosis]
        if new_dx.lower() not in existing_lower:
            # Reassign list for SQLModel to detect JSON modification
            updated_list = list(case_session.user_differential_diagnosis)
            updated_list.append(new_dx)
            case_session.user_differential_diagnosis = updated_list
            case_session.updated_at = datetime.now(timezone.utc)
            db_session.add(case_session)
            db_session.commit()

    return RedirectResponse(url=f"/session/{session_id}", status_code=303)

@router.post("/{session_id}/ddx/remove")
def remove_ddx(session_id: int, diagnosis: str = Form(...), db_session: Session = Depends(get_session)):
    case_session = db_session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Find the diagnosis to remove, case-insensitively, but remove the original
    dx_to_remove = None
    for dx in case_session.user_differential_diagnosis:
        if dx.lower() == diagnosis.lower():
            dx_to_remove = dx
            break
    
    if dx_to_remove:
        updated_list = list(case_session.user_differential_diagnosis)
        updated_list.remove(dx_to_remove)
        case_session.user_differential_diagnosis = updated_list
        case_session.updated_at = datetime.now(timezone.utc)
        db_session.add(case_session)
        db_session.commit()

    return RedirectResponse(url=f"/session/{session_id}", status_code=303)