from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
import random

from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.core.database import get_session
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
]

REASONING_BUCKETS = [
    "subjective_clues",
    "objective_clues",
    "assessment_clues",
    "tests_to_consider",
    "interventions_to_consider",
]


def _normalize(text: str) -> str:
    return text.strip().lower()


def _contains_case_insensitive(items: list[str], target: str) -> bool:
    target_norm = _normalize(target)
    return any(_normalize(item) == target_norm for item in items)


def _find_case_insensitive(items: list[str], target: str) -> str | None:
    target_norm = _normalize(target)
    for item in items:
        if _normalize(item) == target_norm:
            return item
    return None


def _unique_case_insensitive(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_items: list[str] = []
    for item in items:
        norm = _normalize(item)
        if norm not in seen:
            seen.add(norm)
            unique_items.append(item)
    return unique_items


def _clue_exists_in_any_bucket(case_session: CaseStudySession, clue: str) -> bool:
    for bucket_name in REASONING_BUCKETS:
        bucket_items = getattr(case_session, bucket_name, [])
        if _contains_case_insensitive(bucket_items, clue):
            return True
    return False


def _red_flag_text(flag) -> str:
    """
    Supports either:
    - plain string red flags
    - Pydantic objects like RedFlagItem with fields such as:
      clue / point / flag / term / name
    """
    if isinstance(flag, str):
        return flag

    for attr in ("clue", "point", "flag", "term", "name"):
        value = getattr(flag, attr, None)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return str(flag)


@router.get("/{session_id}")
def session_player(
    session_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    case_session = session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")

    case_study = session.get(CaseStudy, case_session.case_study_id)
    if not case_study:
        raise HTTPException(status_code=404, detail="Case study not found for this session")

    case_data = CaseStudySchema.model_validate_json(case_study.raw_json)

    suggestions = [dx.diagnosis for dx in case_data.model_differential]
    distractors = [
        "Asthma",
        "Pneumonia",
        "Costochondritis",
        "Pulmonary Embolism",
        "Panic Attack",
        "Aortic Dissection",
        "Pericarditis",
        "Myocarditis",
        "Peptic Ulcer Disease",
        "Cholecystitis",
        "Pneumothorax",
    ]

    random.seed(session_id)
    selected_distractors = random.sample(distractors, 5)
    suggestions.extend(selected_distractors)
    suggestions = _unique_case_insensitive(suggestions)
    random.shuffle(suggestions)

    user_dx_lower = [_normalize(dx) for dx in case_session.user_differential_diagnosis]
    available_suggestions = [s for s in suggestions if _normalize(s) not in user_dx_lower]

    flagged_lookup = {_normalize(item) for item in case_session.red_flag_clues}
    selected_clues_lookup = set()
    for bucket_name in REASONING_BUCKETS:
        selected_clues_lookup.update(_normalize(item) for item in getattr(case_session, bucket_name, []))

    context = {
        "request": request,
        "session": case_session,
        "case": case_data,
        "suggestions": available_suggestions,
        "flagged_lookup": flagged_lookup,
        "selected_clues_lookup": selected_clues_lookup,
    }

    if case_session.current_stage == 5:
        user_dx_set = {_normalize(dx) for dx in case_session.user_differential_diagnosis}
        model_dx_set = {_normalize(dx.diagnosis) for dx in case_data.model_differential}

        correct_matches = [
            dx for dx in case_session.user_differential_diagnosis
            if _normalize(dx) in model_dx_set
        ]
        extra_diagnoses = [
            dx for dx in case_session.user_differential_diagnosis
            if _normalize(dx) not in model_dx_set
        ]
        missed_diagnoses = [
            dx.diagnosis for dx in case_data.model_differential
            if _normalize(dx.diagnosis) not in user_dx_set
        ]

        model_red_flag_texts = [_red_flag_text(flag) for flag in case_data.red_flags]
        user_flag_set = {_normalize(flag) for flag in case_session.red_flag_clues}
        model_flag_set = {_normalize(flag) for flag in model_red_flag_texts}

        correct_flags = [
            flag for flag in case_session.red_flag_clues
            if _normalize(flag) in model_flag_set
        ]
        missed_flags = [
            flag for flag in model_red_flag_texts
            if _normalize(flag) not in user_flag_set
        ]
        extra_flags = [
            flag for flag in case_session.red_flag_clues
            if _normalize(flag) not in model_flag_set
        ]

        context["review"] = {
            "correct_matches": correct_matches,
            "extra_diagnoses": extra_diagnoses,
            "missed_diagnoses": missed_diagnoses,
            "correct_flags": correct_flags,
            "missed_flags": missed_flags,
            "extra_flags": extra_flags,
        }

    return templates.TemplateResponse(
        request=request,
        name="session/player.html",
        context=context,
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
        case_session.updated_at = datetime.now(timezone.utc)
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
def add_to_bucket(
    session_id: int,
    bucket_name: BucketName,
    clue: str = Form(...),
    db_session: Session = Depends(get_session),
):
    case_session = db_session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")

    new_clue = clue.strip()
    if new_clue:
        bucket_list = getattr(case_session, bucket_name)
        if not _contains_case_insensitive(bucket_list, new_clue):
            updated_list = list(bucket_list)
            updated_list.append(new_clue)
            setattr(case_session, bucket_name, updated_list)
            case_session.updated_at = datetime.now(timezone.utc)
            db_session.add(case_session)
            db_session.commit()

    return RedirectResponse(url=f"/session/{session_id}", status_code=303)


@router.post("/{session_id}/bucket/{bucket_name}/remove")
def remove_from_bucket(
    session_id: int,
    bucket_name: BucketName,
    clue: str = Form(...),
    db_session: Session = Depends(get_session),
):
    case_session = db_session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")

    bucket_list = getattr(case_session, bucket_name)
    clue_to_remove = _find_case_insensitive(bucket_list, clue)

    if clue_to_remove:
        updated_list = list(bucket_list)
        updated_list.remove(clue_to_remove)
        setattr(case_session, bucket_name, updated_list)

        flag_match = _find_case_insensitive(case_session.red_flag_clues, clue_to_remove)
        if flag_match:
            updated_flags = list(case_session.red_flag_clues)
            updated_flags.remove(flag_match)
            case_session.red_flag_clues = updated_flags

        case_session.updated_at = datetime.now(timezone.utc)
        db_session.add(case_session)
        db_session.commit()

    return RedirectResponse(url=f"/session/{session_id}", status_code=303)


@router.post("/{session_id}/bucket/{bucket_name}/clear")
def clear_bucket(
    session_id: int,
    bucket_name: BucketName,
    db_session: Session = Depends(get_session),
):
    case_session = db_session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")

    bucket_items = getattr(case_session, bucket_name, [])
    flag_items = list(case_session.red_flag_clues)

    for item in bucket_items:
        match = _find_case_insensitive(flag_items, item)
        if match:
            flag_items.remove(match)

    setattr(case_session, bucket_name, [])
    case_session.red_flag_clues = flag_items
    case_session.updated_at = datetime.now(timezone.utc)
    db_session.add(case_session)
    db_session.commit()

    return RedirectResponse(url=f"/session/{session_id}", status_code=303)


@router.post("/{session_id}/red-flag/toggle")
def toggle_red_flag(
    session_id: int,
    clue: str = Form(...),
    db_session: Session = Depends(get_session),
):
    case_session = db_session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")

    cleaned = clue.strip()
    if not cleaned:
        return RedirectResponse(url=f"/session/{session_id}", status_code=303)

    if not _clue_exists_in_any_bucket(case_session, cleaned):
        return RedirectResponse(url=f"/session/{session_id}", status_code=303)

    existing_match = _find_case_insensitive(case_session.red_flag_clues, cleaned)
    updated_flags = list(case_session.red_flag_clues)

    if existing_match:
        updated_flags.remove(existing_match)
    else:
        updated_flags.append(cleaned)

    case_session.red_flag_clues = updated_flags
    case_session.updated_at = datetime.now(timezone.utc)
    db_session.add(case_session)
    db_session.commit()

    return RedirectResponse(url=f"/session/{session_id}", status_code=303)


@router.post("/{session_id}/ddx/add")
def add_ddx(
    session_id: int,
    diagnosis: str = Form(...),
    db_session: Session = Depends(get_session),
):
    case_session = db_session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")

    new_dx = diagnosis.strip()
    if new_dx:
        if not _contains_case_insensitive(case_session.user_differential_diagnosis, new_dx):
            updated_list = list(case_session.user_differential_diagnosis)
            updated_list.append(new_dx)
            case_session.user_differential_diagnosis = updated_list
            case_session.updated_at = datetime.now(timezone.utc)
            db_session.add(case_session)
            db_session.commit()

    return RedirectResponse(url=f"/session/{session_id}", status_code=303)


@router.post("/{session_id}/ddx/remove")
def remove_ddx(
    session_id: int,
    diagnosis: str = Form(...),
    db_session: Session = Depends(get_session),
):
    case_session = db_session.get(CaseStudySession, session_id)
    if not case_session:
        raise HTTPException(status_code=404, detail="Session not found")

    match = _find_case_insensitive(case_session.user_differential_diagnosis, diagnosis)
    if match:
        updated_list = list(case_session.user_differential_diagnosis)
        updated_list.remove(match)
        case_session.user_differential_diagnosis = updated_list
        case_session.updated_at = datetime.now(timezone.utc)
        db_session.add(case_session)
        db_session.commit()

    return RedirectResponse(url=f"/session/{session_id}", status_code=303)