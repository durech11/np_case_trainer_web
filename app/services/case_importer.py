import json
from pathlib import Path
from sqlmodel import Session, select
from pydantic import ValidationError
from app.models.schemas import CaseStudySchema
from app.models.case_study import CaseStudy

# Find the project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CASES_DIR = BASE_DIR / "cases"

def import_local_cases(session: Session):
    """Scans the cases directory and imports valid cases into the DB."""
    if not CASES_DIR.exists():
        return
        
    for json_file in CASES_DIR.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Validate against strict Pydantic schema
            parsed_case = CaseStudySchema.model_validate(data)
            
            # Check if case exists in database
            existing_case = session.exec(
                select(CaseStudy).where(CaseStudy.case_id == parsed_case.case_id)
            ).first()
            
            if not existing_case:
                # Insert into DB
                db_case = CaseStudy(
                    case_id=parsed_case.case_id,
                    title=parsed_case.title,
                    specialty=parsed_case.specialty,
                    difficulty=parsed_case.difficulty,
                    summary=parsed_case.summary,
                    raw_json=parsed_case.model_dump_json()
                )
                session.add(db_case)
                session.commit()
                print(f"Imported new case: {parsed_case.case_id} from {json_file.name}")
            else:
                print(f"Case {parsed_case.case_id} already exists. Skipping.")
                
        except json.JSONDecodeError:
            print(f"Error decoding JSON in {json_file.name}. Skipping.")
        except ValidationError as e:
            print(f"Validation error in {json_file.name}: {e}. Skipping.")
        except Exception as e:
            print(f"Unexpected error processing {json_file.name}: {e}. Skipping.")