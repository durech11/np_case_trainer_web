from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import Field, SQLModel, JSON, Column

class CaseStudySession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    case_study_id: int = Field(foreign_key="casestudy.id")
    
    status: str = Field(default="in_progress") # in_progress, completed
    current_stage: int = Field(default=1)
    
    # Store user's differential diagnoses as a JSON list of strings
    user_differential_diagnosis: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None