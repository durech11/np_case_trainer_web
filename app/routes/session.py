from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from pathlib import Path
from datetime import datetime, timezone
import random
from typing import Literal

from app.core.database import get_session, engine
from app.models.case_session import CaseStudySession
from app.models.case_study import CaseStudy
from app.models.schemas import CaseStudySchema

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

router = APIRouter(prefix="/session", tags=["session"])

BucketName = Literal[
    "subjective_clues",
    "objective_clues",
    "assessment_clues",
    "tests_to_consider",
    "interventions_to_consider",
    "red_flag_clues"
]

@router.get("/{session_id}")
def session_player(session_id: int, request: Request, session: Session = Depends(get_session)):
    case_session = session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    case_study = session.get(CaseStudy, case_session.case_study_id)
    if not case_study:
        raise HTTPException(status_code=404, detail="Case study not found for this session")

    case_data = CaseStudySchema.model_validate_json(case_study.raw_json)
    
    # Generate suggestions for DDx
    suggestions = [dx.diagnosis for dx in case_data.model_differential]
    distractors = [
        "Asthma", "Pneumonia", "Costochondritis", "Pulmonary Embolism", 
        "Panic Attack", "Aortic Dissection", "Pericarditis", "Myocarditis",
        "Peptic Ulcer Disease", "Cholecystitis", "Pneumothorax"
    ]
    random.seed(session_id)
    selected_distractors = random.sample(distractors, 5)
    for d in selected_distractors:
        if d not in suggestions:
            suggestions.append(d)
    random.shuffle(suggestions)
    
    user_dx_lower = [dx.lower() for dx in case_session.user_differential_diagnosis]
    available_suggestions = [s for s in suggestions if s.lower() not in user_dx_lower]

    context = {
        "request": request,
        "session": case_session,
        "case": case_data,
        "suggestions": available_suggestions
    }

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

@router.post("/{session_id}/bucket/{bucket_name}/add")
def add_to_bucket(session_id: int, bucket_name: BucketName, clue: str = Form(...), db_session: Session = Depends(get_session)):
    case_session = db_session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    new_clue = clue.strip()
    if new_clue:
        bucket_list = getattr(case_session, bucket_name)
        existing_lower = [c.lower() for c in bucket_list]
        if new_clue.lower() not in existing_lower:
            updated_list = list(bucket_list)
            updated_list.append(new_clue)
            setattr(case_session, bucket_name, updated_list)
            case_session.updated_at = datetime.now(timezone.utc)
            db_session.add(case_session)
            db_session.commit()

    return RedirectResponse(url=f"/session/{session_id}", status_code=303)

@router.post("/{session_id}/bucket/{bucket_name}/remove")
def remove_from_bucket(session_id: int, bucket_name: BucketName, clue: str = Form(...), db_session: Session = Depends(get_session)):
    case_session = db_session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    bucket_list = getattr(case_session, bucket_name)
    clue_to_remove = None
    for c in bucket_list:
        if c.lower() == clue.lower():
            clue_to_remove = c
            break
    
    if clue_to_remove:
        updated_list = list(bucket_list)
        updated_list.remove(clue_to_remove)
        setattr(case_session, bucket_name, updated_list)
        case_session.updated_at = datetime.now(timezone.utc)
        db_session.add(case_session)
        db_session.commit()

    return RedirectResponse(url=f"/session/{session_id}", status_code=303)

@router.post("/{session_id}/ddx/add")
def add_ddx(session_id: int, diagnosis: str = Form(...), db_session: Session = Depends(get_session)):
    case_session = db_session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    new_dx = diagnosis.strip()
    if new_dx:
        existing_lower = [dx.lower() for dx in case_session.user_differential_diagnosis]
        if new_dx.lower() not in existing_lower:
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